export interface ApiError extends Error {
  response?: {
    data: { detail?: string };
  };
}
