import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({ baseURL: API, timeout: 20000 });

export const getOverview = () => api.get("/overview").then((r) => r.data);
export const listFiles = () => api.get("/files").then((r) => r.data.files);
export const getFile = (name) =>
  api.get(`/files/${encodeURIComponent(name)}`).then((r) => r.data);
export const getValidation = () => api.get("/validate").then((r) => r.data);

export const fileDownloadUrl = (name) =>
  `${API}/files/${encodeURIComponent(name)}/download`;
export const zipDownloadUrl = () => `${API}/download-all`;
