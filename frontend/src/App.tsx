import { FormEvent, useEffect, useMemo, useState } from 'react';
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import {
  createAssessment,
  createFollowUp,
  createPatient,
  createPrediction,
  getDashboardSummary,
  getModelStatus,
  getPatients,
  getPatientHistory,
  getReportUrl,
  getXrayUrl,
  uploadXray,
} from './lib/api';
import type { DashboardSummary, ModelStatus } from './lib/api';
import type { Assessment, FollowUp, Patient, Prediction } from './types';

const emptyPatient = {
  full_name: '',
  age: 50,
  sex: 'Female',
  fracture_type: '',
  side: 'Left',
  anatomical_site: '',
  comorbidities: '',
  smoking: false,
};

const emptyAssessment: Assessment = {
  pain_score: 5,
  rom_score: 60,
  muscle_strength: 3,
  gait_score: 55,
  adherence_pct: 80,
  protein_g: 70,
  calories_kcal: 2000,
  weight_kg: 70,
  xray_grade: 60,
  fracture_displacement: 10,
  ost_open: false,
  notes: '',
};

const emptyFollowUp: FollowUp = {
  weight_kg: 70,
  pain_score: 4,
  gait_score: 60,
  mobility_index: 60,
  adherence_pct: 80,
  notes: '',
};

const assessmentFields: Array<{ key: keyof Assessment; label: string; min: number; max: number; step?: number }> = [
  { key: 'pain_score', label: 'Pain score (0–10)', min: 0, max: 10, step: 0.1 },
  { key: 'rom_score', label: 'Range of motion (0–100)', min: 0, max: 100, step: 1 },
  { key: 'muscle_strength', label: 'Muscle strength (0–5)', min: 0, max: 5, step: 0.1 },
  { key: 'gait_score', label: 'Gait score (0–100)', min: 0, max: 100, step: 1 },
  { key: 'adherence_pct', label: 'Physiotherapy adherence (%)', min: 0, max: 100, step: 1 },
  { key: 'protein_g', label: 'Protein (g/day)', min: 0, max: 500, step: 1 },
  { key: 'calories_kcal', label: 'Calories (kcal/day)', min: 0, max: 10000, step: 10 },
  { key: 'weight_kg', label: 'Weight (kg)', min: 0, max: 500, step: 0.1 },
  { key: 'xray_grade', label: 'Radiographic healing score (0–100)', min: 0, max: 100, step: 1 },
  { key: 'fracture_displacement', label: 'Displacement (%)', min: 0, max: 100, step: 1 },
];

function App() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedId, setSelectedId] = useState<number>();
  const [patientForm, setPatientForm] = useState(emptyPatient);
  const [assessmentForm, setAssessmentForm] = useState<Assessment>(emptyAssessment);
  const [followUpForm, setFollowUpForm] = useState<FollowUp>(emptyFollowUp);
  const [selectedFile, setSelectedFile] = useState<File>();
  const [previewUrl, setPreviewUrl] = useState('');
  const [prediction, setPrediction] = useState<Prediction>();
  const [history, setHistory] = useState<Prediction[]>([]);
  const [status, setStatus] = useState<ModelStatus>();
  const [summary, setSummary] = useState<DashboardSummary>();
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  useEffect(() => {
    void loadInitialData();
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setPrediction(undefined);
      setHistory([]);
      return;
    }
    let current = true;
    void getPatientHistory(selectedId).then((data) => {
      if (!current) return;
      setHistory(data.predictions);
      setPrediction(data.predictions[0]);
    }).catch((reason: unknown) => {
      if (current) setError(errorMessage(reason));
    });
    return () => { current = false; };
  }, [selectedId]);

  useEffect(() => {
    if (!selectedFile) {
      setPreviewUrl('');
      return;
    }
    const url = URL.createObjectURL(selectedFile);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [selectedFile]);

  async function loadInitialData() {
    setBusy('loading');
    setError('');
    try {
      const [patientResult, modelStatus, dashboard] = await Promise.all([
        getPatients(),
        getModelStatus(),
        getDashboardSummary(),
      ]);
      setPatients(patientResult.items);
      setStatus(modelStatus);
      setSummary(dashboard);
      setSelectedId((current) => current ?? patientResult.items[0]?.id);
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setBusy('');
    }
  }

  async function refreshPatients() {
    const result = await getPatients();
    setPatients(result.items);
    setSummary(await getDashboardSummary());
  }

  const selectedPatient = useMemo(
    () => patients.find((patient) => patient.id === selectedId),
    [patients, selectedId],
  );
  const latestAssessment = selectedPatient?.assessments?.[selectedPatient.assessments.length - 1];
  const latestXrayAssessment = selectedPatient?.assessments?.slice().reverse().find((item) => item.id && item.image_path);

  const trajectory = useMemo(() => {
    if (!selectedPatient) return [];
    const points = [
      ...(selectedPatient.assessments ?? []).map((item) => ({
        date: item.visit_date ?? '',
        gait: item.gait_score,
        mobility: item.rom_score,
      })),
      ...(selectedPatient.followups ?? []).map((item) => ({
        date: item.followup_date ?? '',
        gait: item.gait_score,
        mobility: item.mobility_index,
      })),
    ];
    return points.sort((a, b) => a.date.localeCompare(b.date)).map((item, index) => ({
      label: item.date ? new Date(item.date).toLocaleDateString() : `Visit ${index + 1}`,
      gait: item.gait,
      mobility: item.mobility,
    }));
  }, [selectedPatient]);

  const explanationData = prediction?.explanation.map((item) => ({
    feature: item.feature.replace(/_/g, ' '),
    importance: Number(item.importance) * 100,
  })) ?? [];

  async function handleCreatePatient(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy('patient');
    setError('');
    setNotice('');
    try {
      const patient = await createPatient(patientForm);
      setSelectedId(patient.id);
      await refreshPatients();
      setPatientForm(emptyPatient);
      setNotice(`Registered ${patient.full_name}.`);
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setBusy('');
    }
  }

  async function handleRunPrediction(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedPatient) return;
    setBusy('assessment');
    setError('');
    setNotice('');
    try {
      const assessment = await createAssessment(selectedPatient.id, assessmentForm);
      if (selectedFile && assessment.id) await uploadXray(assessment.id, selectedFile);
      const result = await createPrediction({ patient_id: selectedPatient.id, assessment: assessmentForm });
      setPrediction(result);
      setHistory((current) => [result, ...current]);
      setAssessmentForm(emptyAssessment);
      setSelectedFile(undefined);
      await refreshPatients();
      setNotice('Assessment saved and Report estimate is generated successfully.');
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setBusy('');
    }
  }

  async function handleCreateFollowUp(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedPatient) return;
    setBusy('followup');
    setError('');
    setNotice('');
    try {
      await createFollowUp(selectedPatient.id, followUpForm);
      await refreshPatients();
      setFollowUpForm(emptyFollowUp);
      setNotice('Follow-up saved to the patient record.');
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setBusy('');
    }
  }

  function downloadReport() {
    if (!selectedPatient) return;
    window.open(getReportUrl(selectedPatient.id), '_blank', 'noopener,noreferrer');
  }

  const metricCards = [
    ['Recovery estimate', prediction ? `${(prediction.recovery_probability * 100).toFixed(1)}%` : '—'],
    ['Recovery duration', prediction ? `${prediction.predicted_days.toFixed(0)} days` : '—'],
    ['Delayed-risk estimate', prediction ? `${(prediction.delayed_risk * 100).toFixed(1)}%` : '—'],
    ['Saved predictions', summary?.prediction_count ?? 0],
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="sticky top-0 z-10 border-b border-slate-800 bg-slate-950/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Academic research prototype</p>
            <h1 className="text-2xl font-bold text-white">REHAB-TWIN</h1>
          </div>
          <div className="rounded-full border border-amber-400/40 bg-amber-400/10 px-3 py-2 text-xs text-amber-200">
            {status?.prototype_mode ?? status?.demo_mode ? 'Local research mode — no validated model' : 'Unvalidated artifacts — local prototype'}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-6 px-4 py-6">
        {error && <div role="alert" className="rounded-xl border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-200">{error}</div>}
        {notice && <div role="status" className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-4 text-sm text-emerald-200">{notice}</div>}

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {metricCards.map(([label, value]) => (
            <div key={label} className="chart-card p-5">
              <p className="text-xs uppercase tracking-[0.15em] text-slate-400">{label}</p>
              <p className="mt-3 text-2xl font-bold text-white">{value}</p>
            </div>
          ))}
        </section>

        <section className="grid gap-6 xl:grid-cols-[340px_minmax(0,1fr)]">
          <aside className="space-y-6">
            <div className="chart-card p-5">
              <h2 className="text-lg font-semibold">Register patient</h2>
              <form className="mt-4 space-y-3" onSubmit={handleCreatePatient}>
                <FormInput label="Full name" value={patientForm.full_name} required onChange={(value) => setPatientForm({ ...patientForm, full_name: value })} />
                <div className="grid grid-cols-2 gap-3">
                  <FormNumber label="Age" min={0} max={120} value={patientForm.age} onChange={(value) => setPatientForm({ ...patientForm, age: value })} />
                  <label className="block text-sm text-slate-300">
                    <span className="mb-1 block text-xs uppercase text-slate-400">Sex</span>
                    <select value={patientForm.sex} onChange={(event) => setPatientForm({ ...patientForm, sex: event.target.value })} className="field">
                      {['Female', 'Male', 'Other', 'Prefer not to say'].map((value) => <option key={value}>{value}</option>)}
                    </select>
                  </label>
                </div>
                <FormInput label="Fracture type" value={patientForm.fracture_type} required onChange={(value) => setPatientForm({ ...patientForm, fracture_type: value })} />
                <div className="grid grid-cols-2 gap-3">
                  <FormInput label="Anatomical site" value={patientForm.anatomical_site} required onChange={(value) => setPatientForm({ ...patientForm, anatomical_site: value })} />
                  <label className="block text-sm text-slate-300">
                    <span className="mb-1 block text-xs uppercase text-slate-400">Side</span>
                    <select value={patientForm.side} onChange={(event) => setPatientForm({ ...patientForm, side: event.target.value })} className="field">
                      {['Left', 'Right', 'Bilateral', 'Unknown'].map((value) => <option key={value}>{value}</option>)}
                    </select>
                  </label>
                </div>
                <FormInput label="Comorbidities" value={patientForm.comorbidities} onChange={(value) => setPatientForm({ ...patientForm, comorbidities: value })} />
                <label className="flex items-center gap-2 text-sm text-slate-300">
                  <input type="checkbox" checked={patientForm.smoking} onChange={(event) => setPatientForm({ ...patientForm, smoking: event.target.checked })} />
                  Current smoker
                </label>
                <button disabled={busy !== ''} className="button-primary w-full" type="submit">{busy === 'patient' ? 'Saving…' : 'Register patient'}</button>
              </form>
            </div>

            <div className="chart-card p-5">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">Patient records</h2>
                <button className="text-xs text-cyan-300" onClick={() => void loadInitialData()} disabled={busy !== ''}>Refresh</button>
              </div>
              <p className="mt-1 text-xs text-slate-400">{summary?.patient_count ?? patients.length} persisted records</p>
              <div className="mt-4 space-y-2">
                {patients.map((patient) => (
                  <button
                    key={patient.id}
                    onClick={() => { setSelectedId(patient.id); setPrediction(undefined); setError(''); setNotice(''); }}
                    className={`w-full rounded-xl border p-3 text-left ${patient.id === selectedId ? 'border-cyan-500 bg-cyan-500/10' : 'border-slate-700 bg-slate-900'}`}
                  >
                    <span className="block font-medium">{patient.full_name}</span>
                    <span className="mt-1 block text-xs text-slate-400">{patient.age} yrs · {patient.fracture_type}</span>
                  </button>
                ))}
                {!patients.length && <p className="rounded-xl border border-slate-800 p-4 text-sm text-slate-400">{busy === 'loading' ? 'Loading records…' : 'No patient records yet. Register a patient to begin.'}</p>}
              </div>
            </div>
          </aside>

          <div className="space-y-6">
            <section className="chart-card p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold">Patient overview</h2>
                  <p className="text-sm text-slate-400">{selectedPatient ? `${selectedPatient.age} · ${selectedPatient.sex} · ${selectedPatient.side} ${selectedPatient.anatomical_site}` : 'Select or register a patient to start.'}</p>
                </div>
                <button disabled={!selectedPatient} onClick={downloadReport} className="button-secondary">Download patient PDF</button>
              </div>
              {selectedPatient && (
                <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                  <SummaryTile label="Fracture" value={selectedPatient.fracture_type} />
                  <SummaryTile label="Comorbidities" value={selectedPatient.comorbidities || 'None recorded'} />
                  <SummaryTile label="Latest gait" value={latestAssessment?.gait_score ?? '—'} />
                  <SummaryTile label="Latest adherence" value={latestAssessment?.adherence_pct != null ? `${latestAssessment.adherence_pct}%` : '—'} />
                </div>
              )}
            </section>

            <div className="grid gap-6 lg:grid-cols-2">
              <form className="chart-card p-5" onSubmit={handleRunPrediction}>
                <h2 className="text-lg font-semibold">Clinical assessment</h2>
                <p className="mt-1 text-sm text-slate-400">The assessment is persisted before the estimate is generated.</p>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {assessmentFields.map(({ key, ...field }) => (
                    <FormNumber key={key} {...field} value={Number(assessmentForm[key] ?? 0)} onChange={(value) => setAssessmentForm({ ...assessmentForm, [key]: value })} />
                  ))}
                </div>
                <label className="mt-3 flex items-center gap-2 text-sm text-slate-300">
                  <input type="checkbox" checked={assessmentForm.ost_open} onChange={(event) => setAssessmentForm({ ...assessmentForm, ost_open: event.target.checked })} />
                  Open fracture
                </label>
                <label className="mt-3 block text-sm text-slate-300">
                  <span className="mb-1 block text-xs uppercase text-slate-400">Clinical notes</span>
                  <textarea rows={3} maxLength={4000} value={assessmentForm.notes ?? ''} onChange={(event) => setAssessmentForm({ ...assessmentForm, notes: event.target.value })} className="field" />
                </label>
                <label className="mt-3 block text-sm text-slate-300">
                  <span className="mb-1 block text-xs uppercase text-slate-400">X-ray image (optional, PNG/JPEG up to 12 MB)</span>
                  <input type="file" accept="image/png,image/jpeg" onChange={(event) => setSelectedFile(event.target.files?.[0])} className="block w-full text-sm text-slate-300 file:mr-3 file:rounded-lg file:border-0 file:bg-cyan-700 file:px-3 file:py-2 file:text-white" />
                </label>
                {previewUrl && <img src={previewUrl} alt="Selected X-ray preview" className="mt-3 h-48 w-full rounded-xl border border-slate-700 bg-black object-contain" />}
                <button disabled={!selectedPatient || busy !== ''} className="button-primary mt-4 w-full" type="submit">
                  {busy === 'assessment' ? 'Saving assessment…' : 'Save assessment & generate estimate'}
                </button>
              </form>

              <form className="chart-card p-5" onSubmit={handleCreateFollowUp}>
                <h2 className="text-lg font-semibold">Follow-up tracking</h2>
                <p className="mt-1 text-sm text-slate-400">Save a longitudinal follow-up for the selected patient.</p>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <FormNumber label="Weight (kg)" min={0} max={500} step={0.1} value={followUpForm.weight_kg} onChange={(value) => setFollowUpForm({ ...followUpForm, weight_kg: value })} />
                  <FormNumber label="Pain (0–10)" min={0} max={10} step={0.1} value={followUpForm.pain_score} onChange={(value) => setFollowUpForm({ ...followUpForm, pain_score: value })} />
                  <FormNumber label="Gait score (0–100)" min={0} max={100} value={followUpForm.gait_score} onChange={(value) => setFollowUpForm({ ...followUpForm, gait_score: value })} />
                  <FormNumber label="Mobility index (0–100)" min={0} max={100} value={followUpForm.mobility_index} onChange={(value) => setFollowUpForm({ ...followUpForm, mobility_index: value })} />
                  <FormNumber label="Adherence (%)" min={0} max={100} value={followUpForm.adherence_pct} onChange={(value) => setFollowUpForm({ ...followUpForm, adherence_pct: value })} />
                </div>
                <label className="mt-3 block text-sm text-slate-300">
                  <span className="mb-1 block text-xs uppercase text-slate-400">Follow-up note</span>
                  <textarea rows={3} maxLength={4000} value={followUpForm.notes ?? ''} onChange={(event) => setFollowUpForm({ ...followUpForm, notes: event.target.value })} className="field" />
                </label>
                <button disabled={!selectedPatient || busy !== ''} className="button-secondary mt-4 w-full" type="submit">{busy === 'followup' ? 'Saving…' : 'Save follow-up'}</button>
                <div className="mt-5 border-t border-slate-800 pt-4">
                  <h3 className="text-sm font-semibold">Attached image</h3>
                  {latestXrayAssessment?.id ? (
                    <img
                      src={getXrayUrl(latestXrayAssessment.id)}
                      alt="Most recently uploaded X-ray"
                      className="mt-3 max-h-60 w-full rounded-xl border border-slate-700 bg-black object-contain"
                    />
                  ) : <p className="mt-2 text-sm text-slate-500">No X-ray attached to an assessment.</p>}
                </div>
              </form>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <section className="chart-card p-5">
                <h2 className="text-lg font-semibold">Recovery tracking</h2>
                <div className="mt-3 h-64">
                  {trajectory.length ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={trajectory}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis dataKey="label" stroke="#94a3b8" />
                        <YAxis domain={[0, 100]} stroke="#94a3b8" />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="gait" stroke="#22d3ee" strokeWidth={3} name="Gait" />
                        <Line type="monotone" dataKey="mobility" stroke="#34d399" strokeWidth={3} name="ROM / mobility" />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : <EmptyChart text="Saved assessments and follow-ups appear here." />}
                </div>
              </section>

              <section className="chart-card p-5">
                <h2 className="text-lg font-semibold">Estimate explanation</h2>
                <p className="mt-1 text-xs text-slate-400">Illustrative feature weights only; not SHAP, LIME, or model-derived evidence.</p>
                <div className="mt-3 h-64">
                  {explanationData.length ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={explanationData} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis type="number" stroke="#94a3b8" />
                        <YAxis dataKey="feature" type="category" width={110} stroke="#94a3b8" />
                        <Tooltip />
                        <Bar dataKey="importance" fill="#38bdf8" radius={[0, 8, 8, 0]} name="Illustrative weight (%)" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : <EmptyChart text="Run an assessment to show the contributing recovery factors." />}
                </div>
              </section>
            </div>

            <section className="chart-card p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold">Prediction history</h2>
                  <p className="text-sm text-slate-400">Saved for the selected patient; values reflect the current local estimate.</p>
                </div>
                <span className="text-xs text-slate-500">{history.length} record{history.length === 1 ? '' : 's'}</span>
              </div>
              <div className="mt-4 overflow-x-auto">
                {history.length ? (
                  <table className="w-full min-w-[560px] text-left text-sm">
                    <thead className="text-xs uppercase text-slate-500"><tr><th className="py-2">Created</th><th>Estimate</th><th>Duration</th><th>Delayed-risk estimate</th><th>Mode</th></tr></thead>
                    <tbody>{history.map((item) => (
                      <tr key={item.id} className="border-t border-slate-800">
                        <td className="py-3">{item.created_at ? new Date(item.created_at).toLocaleString() : '—'}</td>
                        <td>{(item.recovery_probability * 100).toFixed(1)}%</td>
                        <td>{item.predicted_days.toFixed(0)} days</td>
                        <td>{(item.delayed_risk * 100).toFixed(1)}%</td>
                        <td>{item.model_label}</td>
                      </tr>
                    ))}</tbody>
                  </table>
                ) : <p className="py-3 text-sm text-slate-500">No estimates have been saved for this patient.</p>}
              </div>
            </section>

           
          </div>
        </section>
      </main>
    </div>
  );
}

function FormInput({ label, value, onChange, required = false }: { label: string; value: string; onChange: (value: string) => void; required?: boolean }) {
  return (
    <label className="block text-sm text-slate-300">
      <span className="mb-1 block text-xs uppercase text-slate-400">{label}</span>
      <input required={required} value={value} onChange={(event) => onChange(event.target.value)} className="field" />
    </label>
  );
}

function FormNumber({ label, value, onChange, min, max, step = 1 }: { label: string; value: number; onChange: (value: number) => void; min: number; max: number; step?: number }) {
  return (
    <label className="block text-sm text-slate-300">
      <span className="mb-1 block text-xs uppercase text-slate-400">{label}</span>
      <input type="number" required min={min} max={max} step={step} value={value} onChange={(event) => onChange(event.target.value === '' ? 0 : Number(event.target.value))} className="field" />
    </label>
  );
}

function SummaryTile({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-4">
      <p className="text-xs uppercase text-slate-400">{label}</p>
      <p className="mt-2 font-medium text-white">{value}</p>
    </div>
  );
}

function EmptyChart({ text }: { text: string }) {
  return <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-slate-700 text-center text-sm text-slate-500">{text}</div>;
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'An unexpected error occurred while contacting the REHAB-TWIN API.';
}

export default App;
