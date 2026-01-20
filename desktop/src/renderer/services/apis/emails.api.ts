const API_BASE_URL = "http://127.0.0.1:3333";

export interface Email {
  id: string;
  thread_id: string;
  subject: string;
  from_address: { name: string | null; email: string };
  to_addresses: Array<{ name: string | null; email: string }>;
  cc_addresses: Array<{ name: string | null; email: string }>;
  date: string;
  body_text: string;
  body_html?: string;
  attachments: Array<{
    filename: string;
    mime_type: string;
    size: number;
    attachment_id: string;
  }>;
  labels: string[];
  snippet?: string;
}

export interface EmailThread {
  thread_id: string;
  subject: string;
  emails: Email[];
  participants: Array<{ name: string | null; email: string }>;
  last_message_date: string;
  unread_count: number;
}

export interface EmailListResponse {
  emails: Email[];
  total: number;
  page: number;
  page_size: number;
}

export async function getEmails(
  maxResults: number = 50,
  query?: string,
  pageToken?: string
): Promise<EmailListResponse> {
  const params = new URLSearchParams({
    max_results: maxResults.toString(),
  });
  if (query) params.append("query", query);
  if (pageToken) params.append("page_token", pageToken);

  const response = await fetch(`${API_BASE_URL}/emails?${params}`);

  if (!response.ok) {
    throw new Error("Erreur lors de la récupération des emails");
  }

  return response.json();
}

export async function getEmail(emailId: string): Promise<Email> {
  const response = await fetch(`${API_BASE_URL}/emails/${emailId}`);

  if (!response.ok) {
    throw new Error("Erreur lors de la récupération de l'email");
  }

  return response.json();
}

export async function getThreads(
  maxResults: number = 50,
  query?: string
): Promise<EmailThread[]> {
  const params = new URLSearchParams({
    max_results: maxResults.toString(),
  });
  if (query) params.append("query", query);

  const response = await fetch(`${API_BASE_URL}/threads?${params}`);

  if (!response.ok) {
    throw new Error("Erreur lors de la récupération des threads");
  }

  return response.json();
}

export async function getThread(threadId: string): Promise<EmailThread> {
  const response = await fetch(`${API_BASE_URL}/threads/${threadId}`);

  if (!response.ok) {
    throw new Error("Erreur lors de la récupération du thread");
  }

  return response.json();
}

export async function archiveEmail(emailId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/emails/${emailId}/archive`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Erreur lors de l'archivage");
  }
}

export async function markAsRead(emailId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/emails/${emailId}/read`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Erreur lors du marquage comme lu");
  }
}

export async function syncEmails(
  maxResults: number = 100,
  force: boolean = false
): Promise<any> {
  const params = new URLSearchParams({
    max_results: maxResults.toString(),
    force: force.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/emails/sync?${params}`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Erreur lors de la synchronisation");
  }

  return response.json();
}
