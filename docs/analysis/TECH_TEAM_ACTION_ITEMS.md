# ДЕЙСТВИЯ ДЛЯ ТЕХНИЧЕСКОЙ КОМАНДЫ
## Как модифицировать план для HR-безопасного внедрения

**Дата:** 2025-10-25
**Адресовано:** CTO, Backend Lead, Frontend Lead
**Статус:** ACTIONABLE TASKS

---

## РЕЗЮМЕ

**План качества:** ✅ 95% хороший на техническом уровне
**Недостающие части:** ❌ HR-валидация и Legal-проверка
**Добавить:** 5 компонентов для безопасного использования

---

## КОМПЛЕКТ ИЗМЕНЕНИЙ К ПЛАНУ

### 1️⃣ HR Validator Module (КРИТИЧНО)

**Файл:** `backend/core/hr_validator.py` (новый модуль)
**Время:** 8-10 часов
**Приоритет:** 🔴 КРИТИЧЕСКИЙ
**Блокирует:** Production deployment

#### Что разработать:

```python
class HRValidator:
    """Валидация профиля против HR-реальности"""

    def validate_against_reality(self, profile: Dict) -> ValidationResult:
        """
        Главный метод валидации.
        Проверяет профиль на соответствие реальности А101.
        """
        errors = []
        warnings = []

        # Проверка 1: Иерархия (КРИТИЧНО)
        errors.extend(self._validate_hierarchy(profile))

        # Проверка 2: KPI (КРИТИЧНО)
        warnings.extend(self._validate_kpi(profile))

        # Проверка 3: Требования (ВЫСОКИЙ ПРИОРИТЕТ)
        errors.extend(self._check_discrimination(profile))
        warnings.extend(self._check_market_reality(profile))

        return ValidationResult(
            errors=errors,
            warnings=warnings,
            can_use=len(errors) == 0,
            summary=self._generate_summary(errors, warnings)
        )

    def _validate_hierarchy(self, profile: Dict) -> List[str]:
        """Проверка иерархии против реальной оргструктуры"""
        errors = []

        # Получить реальные данные
        actual_position = self._find_position_in_org(
            profile["position"],
            profile["department"]
        )

        if not actual_position:
            errors.append(
                f"Position '{profile['position']}' not found in department '{profile['department']}'"
            )
            return errors

        # Проверить подчинение
        if profile.get("reports_to") != actual_position.get("reports_to"):
            errors.append(
                f"Reporting line mismatch: "
                f"Profile says '{profile.get('reports_to')}', "
                f"Actual is '{actual_position.get('reports_to')}'"
            )

        # Проверить количество подчиненных
        if profile.get("direct_reports", 0) != len(actual_position.get("subordinates", [])):
            errors.append(
                f"Direct reports count mismatch: "
                f"Profile says {profile.get('direct_reports')}, "
                f"Actual is {len(actual_position.get('subordinates', []))}"
            )

        return errors

    def _validate_kpi(self, profile: Dict) -> List[str]:
        """Проверка KPI на реалистичность"""
        warnings = []

        # Если KPI Generic - это warning
        kpi_list = profile.get("kpi", [])
        for kpi in kpi_list:
            if self._is_generic_kpi(kpi):
                warnings.append(
                    f"KPI '{kpi}' appears to be generic. "
                    f"Recommend discussing with department head."
                )

        # Проверить is_measurable
        for kpi in kpi_list:
            if not self._is_measurable(kpi):
                warnings.append(
                    f"KPI '{kpi}' may not be measurable. "
                    f"Clarify metric definition before using."
                )

        return warnings

    def _check_discrimination(self, profile: Dict) -> List[str]:
        """Проверка требований на дискриминацию"""
        errors = []

        requirements = profile.get("requirements", {})

        # Проверки
        if self._requires_age(requirements):
            errors.append("ERROR: Age discrimination - cannot require specific age")

        if self._requires_only_citizen(requirements):
            errors.append("WARNING: May violate immigration law")

        if self._requires_specific_vendor_cert(requirements):
            warnings.append("Consider accepting equivalent certifications")

        return errors

    def _check_market_reality(self, profile: Dict) -> List[str]:
        """Проверка требований на соответствие рынку"""
        warnings = []

        # Проверить требуемый опыт
        experience = profile.get("experience_required")
        if experience and experience > 5:
            warnings.append(
                f"High experience requirement ({experience} years) "
                f"may limit candidate pool. Consider market data for 2025."
            )

        # Проверить образование
        education = profile.get("education")
        if education and education.startswith("Only"):
            warnings.append(
                f"Strict education requirement may exclude qualified candidates. "
                f"Consider accepting equivalent background."
            )

        return warnings
```

#### Интеграция в ProfileGenerator:

```python
# В methods профиля

async def generate_and_validate_profile(self, department: str, position: str) -> Dict:
    """Generate profile with mandatory HR validation"""

    # 1. Generate
    variables = self.data_loader.prepare_langfuse_variables(...)
    profile = await self.llm_client.generate_profile_from_langfuse(...)

    # 2. 🔥 НОВОЕ: HR Validation (обязательное)
    from backend.core.hr_validator import HRValidator
    validator = HRValidator()

    validation = validator.validate_against_reality(profile)

    # 3. Если есть критичные ошибки - не отправляем
    if validation.errors:
        logger.error(f"HR Validation FAILED: {validation.errors}")
        return {
            "success": False,
            "profile": None,
            "validation_errors": validation.errors,
            "note": "Profile requires manual correction before use"
        }

    # 4. Если есть warnings - логируем
    if validation.warnings:
        logger.warning(f"HR Validation Warnings: {validation.warnings}")

    # 5. Возвращаем профиль с результатами валидации
    return {
        "success": True,
        "profile": profile,
        "validation": validation,
        "next_step": "Review with department head and Legal"
    }
```

---

### 2️⃣ KPI Review & Approval Flow (КРИТИЧНО)

**Файл:** `backend/api/kpi_review.py` (новый endpoint)
**Время:** 6-8 часов
**Приоритет:** 🔴 КРИТИЧЕСКИЙ

#### Что разработать:

```python
# backend/api/kpi_review.py

@router.post("/kpi/review")
async def submit_kpi_for_review(
    profile_id: str,
    department_head_id: str,
    legal_reviewer_id: str,
    user: User = Depends(get_current_user)
) -> Dict:
    """
    Submit KPI for formal review.

    Flow:
    1. HR Specialist fills in form
    2. Department Head reviews & approves
    3. Legal reviews & approves
    4. Only then KPI can be used
    """

    # 1. Create review task
    review_task = {
        "profile_id": profile_id,
        "submitted_by": user.id,
        "submitted_at": datetime.now(),
        "status": "pending_department_head",
        "approvals": []
    }

    # 2. Send to department head
    await notify_user(
        user_id=department_head_id,
        message=f"KPI review required for profile {profile_id}",
        action_url=f"/kpi/review/{profile_id}"
    )

    return {"review_task_id": review_task["id"], "status": "pending"}


@router.post("/kpi/approve/{review_task_id}")
async def approve_kpi(
    review_task_id: str,
    approval_type: str,  # "department_head" or "legal"
    user: User = Depends(get_current_user)
) -> Dict:
    """
    Approve KPI at a stage.

    Flow:
    1. Department Head approves content
    2. Legal approves compliance
    3. Only then mark as "ready to use"
    """

    review_task = db.get_review_task(review_task_id)

    # Check authorization
    if approval_type == "department_head":
        # Verify user is the department head
        pass
    elif approval_type == "legal":
        # Verify user is from legal
        pass

    # Add approval
    review_task["approvals"].append({
        "type": approval_type,
        "approved_by": user.id,
        "approved_at": datetime.now(),
        "notes": request.json.get("notes", "")
    })

    # Check if all approvals complete
    if len(review_task["approvals"]) >= 2:  # Both reviews
        review_task["status"] = "approved"
        review_task["ready_to_use"] = True

    db.update_review_task(review_task_id, review_task)

    return {"status": review_task["status"], "approvals": review_task["approvals"]}


@router.get("/kpi/review-status/{profile_id}")
async def get_kpi_review_status(profile_id: str) -> Dict:
    """Get current review status for profile KPI"""
    review_task = db.get_review_task_for_profile(profile_id)
    return {
        "profile_id": profile_id,
        "status": review_task["status"],
        "pending_approval": review_task.get("pending_approval"),
        "approvals": review_task.get("approvals", []),
        "ready_to_use": review_task.get("ready_to_use", False)
    }
```

---

### 3️⃣ Profile Usage Restrictions (ВАЖНО)

**Файл:** `backend/models/database.py` (добавить поле)
**Время:** 4-6 часов
**Приоритет:** 🟠 ВЫСОКИЙ

#### Что добавить:

```python
# backend/models/database.py

class JobProfile(Base):
    __tablename__ = "job_profiles"

    id: str = Column(String, primary_key=True)
    # ... существующие поля ...

    # 🔥 НОВОЕ: Статус готовности к использованию
    approval_status: str = Column(String, default="draft")  # draft, under_review, approved, rejected

    # HR Validation
    hr_validation_status: str = Column(String)  # pending, passed, failed
    hr_validation_errors: List[str] = Column(JSON)
    hr_validation_date: datetime = Column(DateTime)
    hr_validated_by: str = Column(String)  # User ID

    # Department Head Review
    dept_head_review_status: str = Column(String)  # pending, approved, rejected
    dept_head_review_notes: str = Column(String)
    dept_head_review_date: datetime = Column(DateTime)
    dept_head_reviewed_by: str = Column(String)

    # Legal Review
    legal_review_status: str = Column(String)  # pending, approved, rejected
    legal_review_notes: str = Column(String)
    legal_review_date: datetime = Column(DateTime)
    legal_reviewed_by: str = Column(String)

    # Approved Date (when profile can be used)
    approved_date: datetime = Column(DateTime)

    # Version tracking
    version: int = Column(Integer, default=1)
    changes_history: List[Dict] = Column(JSON)  # Track all modifications


# Helper method
def is_approved_for_use(profile: JobProfile) -> bool:
    """Check if profile is approved for HR use"""
    return (
        profile.approval_status == "approved" and
        profile.hr_validation_status == "passed" and
        profile.dept_head_review_status == "approved" and
        profile.legal_review_status == "approved"
    )
```

#### Restriction in API:

```python
# backend/api/profiles.py

@router.get("/profiles/{profile_id}/use")
async def get_profile_for_use(profile_id: str) -> Dict:
    """Get profile for actual use (hiring, evaluation, etc)"""
    profile = db.get_profile(profile_id)

    # Check if profile is approved
    if not is_approved_for_use(profile):
        return {
            "success": False,
            "profile": None,
            "message": f"Profile not approved for use",
            "approval_status": {
                "overall": profile.approval_status,
                "hr_validation": profile.hr_validation_status,
                "dept_head_review": profile.dept_head_review_status,
                "legal_review": profile.legal_review_status
            },
            "next_steps": "Contact HR for approval status"
        }

    # Profile is approved - return it
    return {
        "success": True,
        "profile": profile,
        "approved_date": profile.approved_date,
        "valid_until": profile.approved_date + timedelta(days=365),
        "note": "Profile is approved for use until next update"
    }
```

---

### 4️⃣ Documentation & Compliance Module (ВЫСОКИЙ ПРИОРИТЕТ)

**Файл:** `backend/core/compliance_checker.py` (новый модуль)
**Время:** 10-12 часов
**Приоритет:** 🟠 ВЫСОКИЙ

#### Что разработать:

```python
# backend/core/compliance_checker.py

class ComplianceChecker:
    """
    Check profiles for legal compliance.

    Checks against:
    - Russian Labor Code (ТК РФ)
    - Anti-discrimination laws
    - Employment practices
    """

    # List of red flags / prohibited requirements
    PROHIBITED_REQUIREMENTS = [
        # Age-related
        {"pattern": r"\d+-\d+\s*years?\s*old", "reason": "Age discrimination"},
        {"pattern": r"молод[ой|ая]", "reason": "Age discrimination"},
        {"pattern": r"30\s*years\s*or\s*less", "reason": "Age discrimination"},

        # Gender-related
        {"pattern": r"woman|female|мужчина", "reason": "Gender discrimination"},

        # Citizenship
        {"pattern": r"Russian citizen only", "reason": "May violate immigration law"},

        # Sexual orientation / marital status
        {"pattern": r"married|single|family", "reason": "Personal life discrimination"},

        # Health/disability
        {"pattern": r"no health issues", "reason": "Disability discrimination"},
    ]

    def check_compliance(self, profile: Dict) -> ComplianceResult:
        """Main compliance check"""
        issues = []

        # Check requirements section
        requirements_text = str(profile.get("requirements", ""))
        issues.extend(self._check_discriminatory_language(requirements_text))

        # Check education
        issues.extend(self._check_education(profile.get("education", "")))

        # Check experience
        issues.extend(self._check_experience(profile.get("experience_required", "")))

        # Check other sections for subtle discrimination
        issues.extend(self._check_all_fields(profile))

        return ComplianceResult(
            passed=len(issues) == 0,
            issues=issues,
            summary=self._generate_compliance_summary(issues)
        )

    def _check_discriminatory_language(self, text: str) -> List[Dict]:
        """Check for discriminatory language"""
        issues = []

        for requirement in self.PROHIBITED_REQUIREMENTS:
            if re.search(requirement["pattern"], text, re.IGNORECASE):
                issues.append({
                    "severity": "error",
                    "requirement": requirement["pattern"],
                    "reason": requirement["reason"],
                    "action": "Remove this requirement"
                })

        return issues

    def _check_education(self, education: str) -> List[Dict]:
        """Check education requirements"""
        issues = []

        if education.startswith("Only"):
            issues.append({
                "severity": "warning",
                "field": "education",
                "issue": f"Overly strict education requirement: '{education}'",
                "recommendation": "Consider accepting equivalent background"
            })

        if "specific university" in education.lower():
            issues.append({
                "severity": "error",
                "field": "education",
                "issue": "Cannot require specific university",
                "reason": "Discriminatory practice"
            })

        return issues

    def _check_experience(self, experience_str: str) -> List[Dict]:
        """Check experience requirements"""
        issues = []

        # Extract number if present
        match = re.search(r"(\d+)\+?\s*years?", experience_str)
        if match:
            years = int(match.group(1))
            if years > 5:
                issues.append({
                    "severity": "warning",
                    "field": "experience",
                    "issue": f"High experience requirement: {years}+ years",
                    "note": "May limit candidate pool. Check market data for 2025."
                })

        return issues

    def _check_all_fields(self, profile: Dict) -> List[Dict]:
        """Check all text fields for subtle discrimination"""
        issues = []

        for field, value in profile.items():
            if isinstance(value, str):
                # Check for subtle gender coding
                if any(word in value.lower() for word in ["aggressive", "competitive", "ambitious", "young"]):
                    issues.append({
                        "severity": "warning",
                        "field": field,
                        "issue": "May have subtle gender bias",
                        "text": value[:100],
                        "recommendation": "Review for neutral language"
                    })

        return issues
```

---

### 5️⃣ Audit Trail & Versioning (СРЕДНИЙ ПРИОРИТЕТ)

**Файл:** `backend/core/audit_log.py` (новый модуль)
**Время:** 6-8 часов
**Приоритет:** 🟡 СРЕДНИЙ

#### Что разработать:

```python
# backend/core/audit_log.py

class AuditLog:
    """Track all changes to profiles for legal compliance"""

    def log_action(
        self,
        profile_id: str,
        action: str,  # "created", "modified", "validated", "approved"
        user_id: str,
        changes: Dict = None,
        notes: str = None
    ):
        """Log an action with full context"""

        log_entry = {
            "profile_id": profile_id,
            "action": action,
            "user_id": user_id,
            "timestamp": datetime.now(),
            "changes": changes,
            "notes": notes,
            "ip_address": get_client_ip(),  # For security
        }

        db.insert_audit_log(log_entry)

    def get_profile_history(self, profile_id: str) -> List[Dict]:
        """Get complete history of profile changes"""
        return db.query_audit_logs({"profile_id": profile_id})

    def generate_change_report(self, profile_id: str) -> str:
        """Generate human-readable report of all changes"""
        history = self.get_profile_history(profile_id)

        report = f"PROFILE CHANGE HISTORY: {profile_id}\n"
        report += "=" * 50 + "\n\n"

        for entry in history:
            report += f"[{entry['timestamp']}] {entry['action'].upper()}\n"
            report += f"By: {entry['user_id']}\n"
            if entry['notes']:
                report += f"Notes: {entry['notes']}\n"
            if entry['changes']:
                report += f"Changes:\n"
                for field, (old, new) in entry['changes'].items():
                    report += f"  {field}: '{old}' → '{new}'\n"
            report += "\n"

        return report
```

---

## ПЛАН ВНЕДРЕНИЯ

### Фаза 1: Core Modules (Неделя 1)

**День 1-3: HR Validator**
```
- Design and implement HRValidator class
- Unit tests coverage >= 80%
- Integration with ProfileGenerator
- Testing with sample profiles
```

**День 4-5: KPI Review Flow**
```
- Design endpoints for KPI review
- Implement approval workflow
- Notification system
- Database schema updates
```

**День 6-7: Wrap up Phase 1**
```
- Code review
- Documentation
- Integration tests
```

### Фаза 2: Compliance & Audit (Неделя 2)

**День 8-9: Compliance Checker**
```
- Implement ComplianceChecker
- Add dictionary of prohibited requirements
- Unit tests
```

**День 10-11: Audit Trail**
```
- Implement AuditLog
- Database schema for audit
- History visualization endpoints
```

**День 12-13: Refinement**
```
- Integration testing
- Documentation
- Training materials
```

### Фаза 3: Testing & Documentation (Неделя 3)

**День 14-16: Full Integration Testing**
```
- End-to-end tests for full workflow
- Load testing
- Security review
```

**День 17-18: Documentation**
```
- API documentation
- Usage guides for HR
- Training materials
```

**День 19-20: Production Deployment**
```
- Staging environment testing
- Production deployment
- Monitoring setup
```

---

## API ENDPOINTS SUMMARY

```
POST   /profiles/generate            → Generate profile (draft)
POST   /profiles/{id}/validate-hr    → HR validation
GET    /profiles/{id}/validation     → Get validation results

POST   /kpi/review                   → Submit KPI for review
POST   /kpi/approve/{id}             → Approve/reject KPI
GET    /kpi/review-status/{id}       → Check review status

GET    /profiles/{id}/use            → Get approved profile for use
GET    /profiles/{id}/compliance     → Get compliance check results

GET    /profiles/{id}/history        → Get change history
GET    /audit/report/{id}            → Generate audit report
```

---

## METRICS TO TRACK

```
1. Validation:
   - % profiles passing HR validation on first try
   - Average time in review queue
   - Most common validation errors

2. Quality:
   - % profiles using generic KPI
   - % profiles modified after first version
   - Average number of revisions per profile

3. Legal:
   - % profiles with compliance issues
   - Types of compliance issues found
   - Time to legal approval

4. Usage:
   - % profiles actually used (not sitting in draft)
   - Time from generation to use
   - Profile update frequency
```

---

## TESTING CHECKLIST

- [ ] HR Validator catches all known issues
- [ ] KPI approval workflow blocks unapproved usage
- [ ] Compliance checker identifies discriminatory language
- [ ] Audit trail captures all changes
- [ ] API restrictions prevent unapproved profile access
- [ ] Notifications work for all review steps
- [ ] Backwards compatible with existing data

---

**Версия:** 1.0
**Приоритет:** 🔴 КРИТИЧЕСКИЙ
**Дедлайн:** 2-3 недели
**Ответственность:** Tech Lead + Backend Team
