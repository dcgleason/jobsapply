from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class LinkedinCredentials(BaseModel):
    linkedin_email: EmailStr
    linkedin_password: str

class LinkedinConfig(BaseModel):
    credentials: LinkedinCredentials
    headless: bool
    # chromeProfilePath: Optional[str] = None
    location: List[str]
    keywords: List[str]
    experienceLevels: List[str]
    datePosted: List[str]
    jobType: List[str]
    remote: List[str]
    salary: List[str]
    sort: List[str]
    chromeHeadless: bool  # Add the missing field

    # blacklistCompanies: List[str] = []
    # blockCompanies: List[str] = []  # Add the missing field
    # blackListTitles: List[str] = []
    # followCompanies: bool
    # preferredCv: int
    # outputSkippedQuestions: bool
    # useAiAutocomplete: bool
    # onlyApplyCompanies: List[str] = []
    # onlyApplyTitles: List[str] = []
    # blockHiringMember: List[str] = []
    # onlyApplyHiringMember: List[str] = []
    # onlyApplyMaxApplications: List[str] = []
    # onlyApplyMinApplications: List[str] = []
    # onlyApplyJobDescription: List[str] = []
    # blockJobDescription: List[str] = []
    # onlyApplyMimEmployee: List[str] = []
    # onlyApplyLinkedinRecommending: bool
    # onlyApplySkilledBadges: bool  # Rename the field
    # saveBeforeApply: bool
    # messageToHiringManager: Optional[str] = None
    # listNonEasyApplyJobsUrl: bool
    # defaultRadioOption: int
    # answerAllCheckboxes: Optional[bool] = None
    # outputFileType: List[str]

class ApplyDetails(BaseModel):
    userInfo: str  # Include the userInfo field
    config: LinkedinConfig