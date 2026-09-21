export interface PortfolioWebsite {
  id: number;
  business_name: string;
  website_url?: string | null;
  category: string;
  country?: string | null;
  source_url: string;
  status: string;
  scraped_at: string;
  created_at: string;
  updated_at: string;
  error_message?: string | null;
  last_checked_at?: string | null;
  analysis_status?: 'queued' | 'analyzing' | 'completed' | 'failed' | 'idle';
}

export interface PortfolioPaginatedResponse {
  items: PortfolioWebsite[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ScrapeStatus {
  status: 'idle' | 'running' | 'completed' | 'failed';
  total: number;
  processed: number;
  successful: number;
  failed: number;
  progress: number;
  logs?: string[];
  error?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
}

export interface CategorySummary {
  name: string;
  count: number;
}

export interface Stats {
  total_portfolios: number;
  total_categories: number;
  total_countries: number;
  last_scraped_at?: string | null;
  categories_summary: CategorySummary[];
}

export interface HealthStatus {
  status: string;
  app_name: string;
  version: string;
  database: string;
  playwright: string;
}

export interface PrimaryTechnology {
  name: string;
  type: string; // cms, ecommerce, framework, static
  confidence: number;
  confidence_label: string; // Very High, High, Medium, Low
  evidence: string[];
}

export interface TechItem {
  name: string;
  category?: string;
  confidence: number;
  confidence_label?: string;
  evidence: string[];
}

export interface EvidenceItem {
  technology: string;
  category?: string;
  evidence: string;
  confidence: number;
}

export interface WebsiteAnalysis {
  id: number;
  portfolio_id: number;
  website_url: string;
  status: 'queued' | 'analyzing' | 'completed' | 'failed';
  analyzed_at?: string | null;
  page_title?: string | null;
  final_url?: string | null;
  http_status?: number | null;
  primary_technology_name?: string | null;
  primary_technology_type?: string | null;
  primary_technology_confidence?: number | null;
  primary_technology_evidence?: string[] | null;
  primary_technology?: PrimaryTechnology | null;
  analyzer_version?: string;
  technology_stack?: {
    cms?: TechItem | null;
    ecommerce?: TechItem | null;
    frontend_frameworks?: TechItem[];
    javascript_libraries?: TechItem[];
    css_frameworks?: TechItem[];
    frontend?: TechItem[];
    javascript?: TechItem[];
    css?: TechItem[];
    backend?: {
      language: string;
      framework?: string | null;
      status: string;
      confidence: number;
      confidence_label?: string;
      evidence: string[];
    } | null;
    server?: TechItem | null;
    cdn?: TechItem | null;
  } | null;
  infrastructure?: {
    hosting_provider?: {
      name: string;
      confidence: number;
      evidence: string[];
      status?: string;
      reason?: string;
    } | null;
    deployment_platform?: TechItem | null;
    dns?: {
      domain: string;
      a_records: string[];
      cname: string[];
      nameservers: string[];
    } | null;
    ssl?: {
      enabled: boolean;
      version?: string;
      cipher?: string;
      issuer?: string;
      subject?: string;
      not_before?: string;
      not_after?: string;
      san?: string[];
      reason?: string;
    } | null;
  } | null;
  analytics?: TechItem[] | null;
  integrations?: TechItem[] | null;
  metadata_info?: {
    title?: string;
    description?: string;
    keywords?: string;
    viewport?: string;
    canonical_url?: string;
    favicon?: string;
    element_counts?: {
      script_tags: number;
      stylesheet_tags: number;
      images: number;
      iframes: number;
    };
  } | null;
  performance_metrics?: {
    http_response_time_ms: number;
    script_count: number;
    stylesheet_count: number;
    image_count: number;
  } | null;
  evidence?: EvidenceItem[] | null;
  overall_confidence: number;
  error_message?: string | null;
  created_at: string;
}

export interface AnalysisStats {
  total_websites: number;
  analyzed_count: number;
  pending_count: number;
  failed_count: number;
  cms_distribution: Record<string, number>;
  framework_distribution: Record<string, number>;
  hosting_distribution: Record<string, number>;
  top_technologies: Array<{ name: string; count: number }>;
}
