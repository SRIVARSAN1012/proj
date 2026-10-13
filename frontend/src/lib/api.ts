import type { Assessment, FollowUp, Patient, Prediction } from '../types';

const API_BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

type PatientList = {
  items: Patient[];
  page: number;
  page_size: number;
  total: number;
};

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData) && options.body !== undefined) {
    headers.set('Content-Type', 'application/json');
  }
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error('Could not reach the REHAB-TWIN API. Confirm the backend is running on port 8000 and refresh the page.');
    }
    throw error;
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { detail?: string | Array<{ msg?: string }> } | null;
    const detail = Array.isArray(payload?.detail)
      ? payload.detail.map((item) => item.msg).filter(Boolean).join('; ')
      : payload?.detail;
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export function getPatients() {
  return api<PatientList>('/patients');
}

export function createPatient(payload: Omit<Patient, 'id' | 'created_at' | 'assessments' | 'followups'>) {
  return api<Patient>('/patients', { method: 'POST', body: JSON.stringify(payload) });
}

export function createAssessment(patientId: number, payload: Assessment) {
  return api<Assessment>(`/patients/${patientId}/assessments`, { method: 'POST', body: JSON.stringify(payload) });
}

export function createFollowUp(patientId: number, payload: FollowUp) {
  return api<FollowUp>(`/patients/${patientId}/followups`, { method: 'POST', body: JSON.stringify(payload) });
}

export function uploadXray(assessmentId: number, file: File) {
  const body = new FormData();
  body.append('file', file);
  return api<{ status: string; assessment_id: number; image_url: string }>(`/assessments/${assessmentId}/xray`, {
    method: 'POST',
    body,
  });
}

export function createPrediction(payload: { patient_id: number; assessment: Assessment }) {
  return api<Prediction>('/predictions', { method: 'POST', body: JSON.stringify(payload) });
}

export function getModelStatus() {
  return api<ModelStatus>('/model-status');
}

export function getDashboardSummary() {
  return api<DashboardSummary>('/dashboard/summary');
}

export function getPatientHistory(patientId: number) {
  return api<PatientHistory>(`/patients/${patientId}/history`);
}

export function getReportUrl(patientId: number) {
  return `${API_BASE}/reports/${patientId}`;
}

export function getXrayUrl(assessmentId: number) {
  return `${API_BASE}/assessments/${assessmentId}/xray`;
}

export type ModelStatus = {
  status: string;
  demo_mode: boolean;
  radiology_model: string;
  clinical_model: string;
  fusion_model: string;
  last_training: string | null;
  metrics: null;
  notes: string;
};

export type DashboardSummary = {
  patient_count: number;
  assessment_count: number;
  prediction_count: number;
  demo_mode: boolean;
  status: string;
  clinic_notice: string;
};

export type PatientHistory = {
  patient: Patient;
  predictions: Prediction[];
};
