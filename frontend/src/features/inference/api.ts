import api from "../../api/client";

export interface InferencePayload {
  session_id: string;
  input_text: string;
  policy: string;
}

export interface InferenceResult {
  response: string;
  secret_id?: string;
  leak_detected: boolean;
}

export interface SecretMapping {
  secret_id: string;
  session_id: string;
  owner_id: string;
  created_at: string;
  detector_metadata: Record<string, unknown>;
  mapping: Record<string, { label: string; original: string; synthetic: string }>;
}

export const runInference = async (payload: InferencePayload): Promise<InferenceResult> => {
  const { data } = await api.post<InferenceResult>("/v1/inference", payload);
  return data;
};

export const fetchSecret = async (secretId: string): Promise<SecretMapping> => {
  const { data } = await api.get<SecretMapping>(`/v1/secret/${secretId}`);
  return data;
};
