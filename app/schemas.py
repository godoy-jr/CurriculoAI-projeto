from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AnalysisRequest(BaseModel):
    candidate_name: str = Field(default="Candidato", min_length=2, max_length=80)
    resume: str = Field(min_length=80, max_length=12_000)
    job_description: str = Field(min_length=80, max_length=8_000)

    @field_validator("candidate_name", "resume", "job_description")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("O campo não pode estar vazio.")
        return value


class SkillMatch(BaseModel):
    skill: str
    evidence: str


class MissingSkill(BaseModel):
    skill: str
    importance: Literal["baixa", "média", "alta"]
    suggestion: str


class AnalysisResponse(BaseModel):
    match_score: int = Field(ge=0, le=100)
    summary: str
    strengths: list[str]
    matching_skills: list[SkillMatch]
    missing_skills: list[MissingSkill]
    resume_improvements: list[str]
    interview_tips: list[str]
    cover_letter: str
    disclaimer: str = "Análise orientativa gerada por IA; a decisão final deve ser humana."
    mode: Literal["gemini", "demo"] = "gemini"

