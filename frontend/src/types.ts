export type Patient = {
  id: number;
  full_name: string;
  age: number;
  sex: string;
  fracture_type: string;
  side: string;
  anatomical_site: string;
  comorbidities: string;
  smoking: boolean;
  created_at?: string;
  assessments?: Assessment[];
  followups?: FollowUp[];
};

export type Assessment = {
  id?: number;
  visit_date?: string;
  pain_score: number;
  rom_score: number;
  muscle_strength: number;
  gait_score: number;
  adherence_pct: number;
  protein_g: number;
  calories_kcal: number;
  weight_kg: number;
  xray_grade: number;
  fracture_displacement: number;
  ost_open: boolean;
  notes?: string;
  image_path?: string | null;
};

export type FollowUp = {
  id?: number;
  followup_date?: string;
  weight_kg: number;
  pain_score: number;
  gait_score: number;
  mobility_index: number;
  adherence_pct: number;
  notes?: string;
};

export type Prediction = {
  id?: number;
  patient_id?: number;
  recovery_probability: number;
  predicted_days: number;
  delayed_risk: number;
  model_label: string;
  explanation: Array<{ feature: string; importance: number }>;
  notes?: string;
  status?: string;
  created_at?: string;
  warnings?: string[];
};
