import {
  HealthStatus,
  PortfolioWebsite,
  PortfolioPaginatedResponse,
  ScrapeStatus,
  Stats,
  CategorySummary,
} from './types';

const rawApiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
export const API_BASE_URL = rawApiUrl.replace(/\/+$/, '');
const DEFAULT_TIMEOUT_MS = 8000;

/**
 * Fetch wrapper with timeout signal to prevent hanging client requests.
 */
async function fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs: number = DEFAULT_TIMEOUT_MS): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    // Return a 503 response instead of throwing to prevent Next.js dev overlay from catching the fetch error
    return new Response(JSON.stringify({ detail: 'Backend unreachable or request timed out' }), {
      status: 503,
      statusText: 'Service Unavailable',
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

export async function fetchHealth(): Promise<HealthStatus> {
  try {
    const healthUrl = `${API_BASE_URL}/api/health`;
    const res = await fetchWithTimeout(healthUrl, { cache: 'no-store' }, 4000);
    if (!res.ok) {
      console.warn(`[BACKEND HEALTH] URL: ${healthUrl} | Status: ${res.status} | Backend: OFFLINE`);
      return {
        status: 'offline',
        app_name: 'OptiInfo Backend (Offline)',
        version: '1.0.0',
        database: 'disconnected',
        playwright: 'unavailable',
      };
    }
    const data = await res.json();
    const isHealthy = data.status === 'healthy' || data.status === 'ok';
    console.log(`[BACKEND HEALTH] URL: ${healthUrl} | Status: ${res.status} | Backend: ${isHealthy ? 'ONLINE' : 'DEGRADED'}`);
    return {
      status: isHealthy ? 'healthy' : 'degraded',
      app_name: data.app_name || 'OptiInfo Backend',
      version: data.version || '1.0.0',
      database: data.database || 'connected',
      playwright: data.playwright || 'available',
    };
  } catch (error) {
    console.error('[BACKEND HEALTH] Error fetching backend status:', error);
    return {
      status: 'offline',
      app_name: 'OptiInfo Backend (Offline)',
      version: '1.0.0',
      database: 'disconnected',
      playwright: 'unavailable',
    };
  }
}

export async function fetchPortfolios(
  search?: string,
  category?: string,
  page: number = 1,
  limit: number = 25,
  sortBy: string = 'id',
  sortOrder: string = 'asc'
): Promise<PortfolioPaginatedResponse> {
  try {
    const params = new URLSearchParams();
    if (search && search.trim()) params.append('search', search.trim());
    if (category && category !== 'All') params.append('category', category.trim());
    params.append('page', page.toString());
    params.append('limit', limit.toString());
    params.append('sort_by', sortBy);
    params.append('sort_order', sortOrder);

    const res = await fetchWithTimeout(`${API_BASE_URL}/api/portfolios?${params.toString()}`, {
      cache: 'no-store',
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error('Error fetching portfolios:', error);
    return {
      items: [],
      total: 0,
      page: 1,
      limit: limit,
      pages: 1,
    };
  }
}

export async function fetchPortfolioById(id: number): Promise<PortfolioWebsite | null> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/portfolios/${id}`, { cache: 'no-store' });
    if (!res.ok) return null;
    return await res.json();
  } catch (error) {
    return null;
  }
}

export async function deletePortfolioItem(id: number): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/portfolios/${id}`, {
      method: 'DELETE',
    });
    return res.ok;
  } catch (error) {
    return false;
  }
}

export async function fetchCategories(): Promise<CategorySummary[]> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/categories`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (error) {
    return [];
  }
}

export async function fetchStats(): Promise<Stats | null> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/stats`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (error) {
    return null;
  }
}

export async function startScraping(): Promise<{ success: boolean; message: string }> {
  try {
    const res = await fetchWithTimeout(
      `${API_BASE_URL}/api/scrape/start`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      },
      5000
    );

    const data = await res.json();
    if (res.status === 202) {
      return { success: true, message: data.message || 'Scraper started successfully.' };
    } else if (res.status === 409) {
      return { success: false, message: data.detail || 'Scraper is already running.' };
    }
    return { success: false, message: data.detail || 'Failed to start scraper.' };
  } catch (error) {
    return { success: false, message: 'Network error connecting to backend API.' };
  }
}

export async function fetchScrapeStatus(): Promise<ScrapeStatus> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/scrape/status`, { cache: 'no-store' }, 4000);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (error) {
    return {
      status: 'idle',
      total: 0,
      processed: 0,
      successful: 0,
      failed: 0,
      progress: 0,
      error: 'Backend unreachable',
    };
  }
}

// ==========================================
// WEBSITE ANALYSIS ENGINE API METHODS
// ==========================================

export async function triggerAnalysis(portfolioId: number): Promise<{ success: boolean; message: string }> {
  try {
    const res = await fetchWithTimeout(
      `${API_BASE_URL}/api/websites/${portfolioId}/analyze`,
      { method: 'POST', headers: { 'Content-Type': 'application/json' } },
      8000
    );
    if (res.ok) {
      return { success: true, message: 'Website technology analysis queued successfully.' };
    }
    const data = await res.json();
    return { success: false, message: data.detail || 'Failed to queue website analysis.' };
  } catch (error) {
    return { success: false, message: 'Network error connecting to backend API.' };
  }
}

export async function fetchAnalysis(portfolioId: number): Promise<any | null> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/websites/${portfolioId}/analysis`, { cache: 'no-store' });
    if (!res.ok) return null;
    return await res.json();
  } catch (error) {
    return null;
  }
}

export async function fetchAnalysisStatus(portfolioId: number): Promise<{ portfolio_id: number; website_url: string; status: string; error?: string }> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/websites/${portfolioId}/analysis/status`, { cache: 'no-store' });
    if (!res.ok) return { portfolio_id: portfolioId, website_url: '', status: 'idle' };
    return await res.json();
  } catch (error) {
    return { portfolio_id: portfolioId, website_url: '', status: 'idle' };
  }
}

export async function triggerBulkAnalysis(portfolioIds?: number[]): Promise<{ success: boolean; message: string; queued_count: number }> {
  try {
    const res = await fetchWithTimeout(
      `${API_BASE_URL}/api/websites/analyze-bulk`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ portfolio_ids: portfolioIds }),
      },
      10000
    );
    const data = await res.json();
    if (res.ok) {
      return { success: true, message: data.message, queued_count: data.queued_count };
    }
    return { success: false, message: data.detail || 'Failed to bulk queue analysis.', queued_count: 0 };
  } catch (error) {
    return { success: false, message: 'Network error connecting to backend API.', queued_count: 0 };
  }
}

export async function stopBulkAnalysis(): Promise<{ success: boolean; message: string; stopped_count: number }> {
  try {
    const res = await fetchWithTimeout(
      `${API_BASE_URL}/api/websites/analyze-stop`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      },
      8000
    );
    const data = await res.json();
    if (res.ok) {
      return { success: true, message: data.message, stopped_count: data.stopped_count || 0 };
    }
    return { success: false, message: data.detail || 'Failed to stop website analysis.', stopped_count: 0 };
  } catch (error) {
    return { success: false, message: 'Network error connecting to backend API.', stopped_count: 0 };
  }
}

export async function fetchAnalysisStats(): Promise<any | null> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/analysis/stats`, { cache: 'no-store' });
    if (!res.ok) return null;
    return await res.json();
  } catch (error) {
    return null;
  }
}

export async function fetchAnalysesList(skip: number = 0, limit: number = 50): Promise<any[]> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/analyses?skip=${skip}&limit=${limit}`, { cache: 'no-store' });
    if (!res.ok) return [];
    return await res.json();
  } catch (error) {
    return [];
  }
}
