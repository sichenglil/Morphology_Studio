async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, { headers: {'Content-Type': 'application/json'}, ...init })
  if (!response.ok) throw new Error((await response.text()) || `HTTP ${response.status}`)
  return response.json() as Promise<T>
}
export const api = {
  get: <T>(url: string) => request<T>(url),
  post: <T>(url: string, body?: unknown) => request<T>(url, {method: 'POST', body: body === undefined ? undefined : JSON.stringify(body)}),
  patch: <T>(url: string, body: unknown) => request<T>(url, {method: 'PATCH', body: JSON.stringify(body)}),
}
