from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class LinkedinCredentials(BaseModel):
    linkedin_email: EmailStr
    linkedin_password: str

class LinkedinConfig(BaseModel):
    credentials: LinkedinCredentials
    headless: bool
    chromeProfilePath: Optional[str] = None
    location: List[str]
    keywords: List[str]
    experienceLevels: List[str]
    datePosted: List[str]
    jobType: List[str]
    remote: List[str]
    salary: List[str]
    sort: List[str]
    blacklistCompanies: List[str] = []
    blackListTitles: List[str] = []
    followCompanies: bool
    preferredCv: int
    outputSkippedQuestions: bool
    useAiAutocomplete: bool
    onlyApplyCompanies: List[str] = []
    onlyApplyTitles: List[str] = []
    blockHiringMember: List[str] = []
    onlyApplyHiringMember: List[str] = []
    onlyApplyMaxApplications: List[str] = []
    onlyApplyMinApplications: List[str] = []
    onlyApplyJobDescription: List[str] = []
    blockJobDescription: List[str] = []
    onlyApplyMimEmployee: List[str] = []
    onlyApplyLinkedinRecommending: bool
    onlyApplySkilledBages: bool
    saveBeforeApply: bool
    messageToHiringManager: Optional[str] = None
    listNonEasyApplyJobsUrl: bool
    defaultRadioOption: int
    answerAllCheckboxes: Optional[bool] = None
    outputFileType: List[str]

class ApplyDetails(BaseModel):
    email: EmailStr
    phone_country_code: str = Field(..., min_length=1, max_length=4)
    mobile_phone_number: str = Field(..., min_length=5, max_length=15)
    has_technical_experience: bool
    has_teaching_experience: bool
    is_us_citizen: bool
    has_bachelors_degree: bool
    years_experience_servicenow: int
    favorite_technology: str
    reason_for_applying: str
    config: LinkedinConfig
    userInfo: str 
