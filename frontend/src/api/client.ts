import axios, { AxiosHeaders, type InternalAxiosRequestConfig } from "axios";

const api = axios.create({
  baseURL: "/api",
});

type TokenProvider = () => string | null;

let tokenProvider: TokenProvider | null = null;

export const configureTokenProvider = (provider: TokenProvider) => {
  tokenProvider = provider;
};

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (tokenProvider) {
    const token = tokenProvider();
    if (token) {
      if (!config.headers) {
        config.headers = new AxiosHeaders();
      }
      config.headers.set("Authorization", `Bearer ${token}`);
    }
  }
  return config;
});

export default api;
