"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { useAuthStore } from "@/store/auth";

const QUESTION_TYPES = ["mcq", "coding", "sql", "aptitude"];

export default function NewAssessmentPage() {
  const router = useRouter();
  const token = useAuthStore((s) => s.accessToken)!;
  const [title, setTitle] = useState("");
  const [role, setRole] = useState("Backend Engineer");
  const [skills, setSkills] = useState("Python, SQL, REST APIs");
  const [types, setTypes] = useState<string[]>(["mcq", "coding"]);
  const [duration, setDuration] = useState(60);
  const [proctoring, setProctoring] = useState(true);
  const [adaptive, setAdaptive] = useState(false);
  const [generateAi, setGenerateAi] = useState(true);
  const [questionCount, setQuestionCount] = useState(3);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function toggleType(type: string) {
    setTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type],
    );
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (types.length === 0) {
      setError("Select at least one question type");
      return;
    }

    setError("");
    setLoading(true);
    try {
      const assessment = await api.createAssessment(token, {
        title,
        role,
        types,
        duration_minutes: duration,
        proctoring,
        adaptive,
      });

      if (generateAi) {
        await api.generateQuestions(
          token,
          {
            role,
            skills: skills.split(",").map((s) => s.trim()).filter(Boolean),
            difficulty: "medium",
            types,
            count: questionCount,
          },
          assessment.id,
        );
      }

      router.push(`/recruiter/assessments/${assessment.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create assessment");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <Link href="/recruiter" className="text-sm text-muted hover:text-accent">
        ← Back to dashboard
      </Link>
      <h1 className="mt-4 font-sans text-3xl font-extrabold">Create Assessment</h1>

      <form onSubmit={handleSubmit} className="card-panel mt-6 space-y-5">
        <div>
          <label className="mb-1 block text-xs text-muted">Title</label>
          <input className="input-field" value={title} onChange={(e) => setTitle(e.target.value)} required />
        </div>
        <div>
          <label className="mb-1 block text-xs text-muted">Target role</label>
          <input className="input-field" value={role} onChange={(e) => setRole(e.target.value)} required />
        </div>
        <div>
          <label className="mb-1 block text-xs text-muted">Skills (comma-separated)</label>
          <input className="input-field" value={skills} onChange={(e) => setSkills(e.target.value)} />
        </div>
        <div>
          <label className="mb-2 block text-xs text-muted">Question types</label>
          <div className="flex flex-wrap gap-2">
            {QUESTION_TYPES.map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => toggleType(type)}
                className={`rounded border px-3 py-1 text-xs uppercase ${
                  types.includes(type)
                    ? "border-accent bg-accent/10 text-accent"
                    : "border-border text-muted"
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs text-muted">Duration (minutes)</label>
            <input
              className="input-field"
              type="number"
              min={15}
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs text-muted">Questions per type (AI)</label>
            <input
              className="input-field"
              type="number"
              min={1}
              max={10}
              value={questionCount}
              onChange={(e) => setQuestionCount(Number(e.target.value))}
              disabled={!generateAi}
            />
          </div>
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={proctoring} onChange={(e) => setProctoring(e.target.checked)} />
          Enable proctoring
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={adaptive} onChange={(e) => setAdaptive(e.target.checked)} />
          Adaptive difficulty
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={generateAi} onChange={(e) => setGenerateAi(e.target.checked)} />
          Generate questions with AI now
        </label>

        {error && <p className="text-sm text-red">{error}</p>}
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Creating..." : "Create Assessment"}
        </button>
      </form>
    </div>
  );
}
