import type { Email } from "./Email";

export interface EmailListResponse {
  emails: Email[];
  total: number;
  page: number;
  page_size: number;
}
