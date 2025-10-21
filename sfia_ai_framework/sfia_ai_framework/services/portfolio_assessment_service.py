"""
Portfolio Assessment Service - IoC Portfolio Mapping Implementation

This service implements the complete Institute of Coding (IoC) portfolio mapping
methodology for assessing student competencies against SFIA skills and levels.
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import logging
import re
from collections import defaultdict

from ..models.portfolio_models import (
    PortfolioEntry, SupervisorComment, SkillComponentMapping,
    TechnicalAchievementAssessment, ReflectionAssessment,
    GenericResponsibilityAssessment, PortfolioAssessment,
    PortfolioAssessmentSummary, EvidenceQuality, ProficiencyThreshold,
    GenericResponsibilityCharacteristic, PortfolioEntryType,
    PortfolioAnalysisResponse, PortfolioMappingGuidance
)
from ..models.sfia_models import Skill, SkillLevel, ResponsibilityLevel
from ..core.knowledge_graph import SFIAKnowledgeGraph


class PortfolioAssessmentService:
    """
    Service implementing IoC Portfolio Mapping methodology for SFIA assessment
    """
    
    def __init__(self, knowledge_graph: SFIAKnowledgeGraph):
        self.knowledge_graph = knowledge_graph
        self.logger = logging.getLogger(__name__)
        
        # IoC Assessment weights
        self.TECHNICAL_ACHIEVEMENT_WEIGHT = 16
        self.REFLECTION_WEIGHT = 9
        
        # IoC Thresholds
        self.PROFICIENCY_THRESHOLD = 65
        self.COMPETENCY_THRESHOLD = 85
        
        # Generic Responsibility Thresholds (based on IoC methodology)
        self.CORE_CHARACTERISTICS_THRESHOLD = 13  # 80% of 17 core characteristics
        self.CORE_INSTANCES_THRESHOLD = 26        # Average score 2 for core
        self.TOTAL_INSTANCES_THRESHOLD = 44       # 65% overall threshold
    
    async def analyze_portfolio(
        self,
        portfolio_entries: List[Dict[str, Any]],
        supervisor_comments: List[Dict[str, Any]],
        student_info: Dict[str, Any],
        assessor_info: Dict[str, Any],
        suggested_skill: Optional[str] = None,
        suggested_level: Optional[int] = None
    ) -> PortfolioAnalysisResponse:
        """
        Analyze a complete portfolio using IoC methodology
        """
        try:
            # Step 1: Parse portfolio entries
            entries = await self._parse_portfolio_entries(portfolio_entries)
            supervisor_comments_parsed = await self._parse_supervisor_comments(supervisor_comments)
            
            # Step 2: Select appropriate SFIA skill and level
            skill_code, skill_level = await self._select_sfia_skill_and_level(
                entries, suggested_skill, suggested_level
            )
            
            # Step 3: Map portfolio entries to skill components
            component_mappings = await self._map_entries_to_skill_components(
                entries, skill_code, skill_level
            )
            
            # Step 4: Assess technical achievement
            technical_assessment = await self._assess_technical_achievement(
                component_mappings, supervisor_comments_parsed, skill_code, skill_level
            )
            
            # Step 5: Assess reflection
            reflection_assessment = await self._assess_reflection(
                entries, supervisor_comments_parsed
            )
            
            # Step 6: Assess generic responsibility characteristics
            generic_assessments = await self._assess_generic_responsibility_characteristics(
                entries, supervisor_comments_parsed, skill_level
            )
            
            # Step 7: Calculate scores
            technical_weighted = technical_assessment.unweighted_score * self.TECHNICAL_ACHIEVEMENT_WEIGHT
            reflection_weighted = reflection_assessment.unweighted_score * self.REFLECTION_WEIGHT
            total_score = technical_weighted + reflection_weighted
            
            # Step 8: Evaluate generic responsibility thresholds
            generic_pass = await self._evaluate_generic_responsibility_thresholds(generic_assessments)
            
            # Step 9: Determine final assessment
            proficiency_threshold = self._determine_proficiency_threshold(total_score)
            overall_pass = proficiency_threshold != ProficiencyThreshold.DEVELOPING and generic_pass
            
            # Step 10: Create assessment result
            assessment = PortfolioAssessment(
                id=f"assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                student_id=student_info.get('id', ''),
                student_name=student_info.get('name', ''),
                assessor_id=assessor_info.get('id', ''),
                assessor_name=assessor_info.get('name', ''),
                portfolio_entries=entries,
                supervisor_comments=supervisor_comments_parsed,
                selected_skill_code=skill_code,
                selected_skill_level=skill_level,
                skill_component_mappings=component_mappings,
                technical_achievement=technical_assessment,
                reflection_assessment=reflection_assessment,
                generic_responsibility_assessments=generic_assessments,
                technical_weighted_score=technical_weighted,
                reflection_weighted_score=reflection_weighted,
                total_weighted_score=total_score,
                proficiency_threshold=proficiency_threshold,
                overall_pass=overall_pass,
                generic_responsibility_pass=generic_pass,
                placement_organization=student_info.get('placement_organization'),
                academic_institution=student_info.get('academic_institution')
            )
            
            # Create summary
            summary = PortfolioAssessmentSummary(
                assessment_id=assessment.id,
                student_name=assessment.student_name,
                skill_assessed=f"{skill_code} - {await self._get_skill_name(skill_code)}",
                level_assessed=skill_level,
                total_score=total_score,
                proficiency_level=proficiency_threshold,
                pass_status=overall_pass,
                technical_score=technical_weighted,
                reflection_score=reflection_weighted,
                generic_responsibility_pass=generic_pass,
                assessor_name=assessment.assessor_name,
                assessment_date=assessment.assessment_date,
                placement_organization=assessment.placement_organization,
                recommendations=await self._generate_recommendations(assessment)
            )
            
            return PortfolioAnalysisResponse(
                success=True,
                message=f"Portfolio assessment completed: {proficiency_threshold.value}",
                assessment=assessment,
                summary=summary,
                recommendations=summary.recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Portfolio analysis failed: {e}")
            return PortfolioAnalysisResponse(
                success=False,
                message=f"Assessment failed: {str(e)}"
            )
    
    async def _parse_portfolio_entries(self, entries_data: List[Dict[str, Any]]) -> List[PortfolioEntry]:
        """Parse raw portfolio entry data into PortfolioEntry objects"""
        entries = []
        
        for entry_data in entries_data:
            entry = PortfolioEntry(
                id=entry_data.get('id', f"entry_{len(entries)}"),
                date=datetime.strptime(entry_data['date'], '%Y-%m-%d').date(),
                title=entry_data.get('title', ''),
                content=entry_data['content'],
                entry_type=PortfolioEntryType(entry_data.get('type', 'technical_activity')),
                supervisor_verified=entry_data.get('supervisor_verified', False),
                page_reference=entry_data.get('page_reference'),
                url_reference=entry_data.get('url_reference')
            )
            
            # Analyze content for evidence quality
            entry.evidence_quality = await self._assess_evidence_quality(entry.content)
            
            # Extract reflective elements
            entry.reflective_elements = await self._extract_reflective_elements(entry.content)
            
            # Identify professional accountability
            entry.professional_accountability = await self._identify_professional_accountability(entry.content)
            
            entries.append(entry)
        
        return entries
    
    async def _parse_supervisor_comments(self, comments_data: List[Dict[str, Any]]) -> List[SupervisorComment]:
        """Parse supervisor comments"""
        comments = []
        
        for comment_data in comments_data:
            comment = SupervisorComment(
                id=comment_data.get('id', f"comment_{len(comments)}"),
                supervisor_name=comment_data['supervisor_name'],
                supervisor_role=comment_data.get('supervisor_role', ''),
                organization=comment_data.get('organization', ''),
                comment=comment_data['comment'],
                accuracy_confirmation=comment_data.get('accuracy_confirmation', False),
                contextual_evaluation=comment_data.get('contextual_evaluation', False),
                achievement_assessment=comment_data.get('achievement_assessment', ''),
                difficulty_context=comment_data.get('difficulty_context'),
                recommendation=comment_data.get('recommendation')
            )
            comments.append(comment)
        
        return comments
    
    async def _select_sfia_skill_and_level(
        self,
        entries: List[PortfolioEntry],
        suggested_skill: Optional[str] = None,
        suggested_level: Optional[int] = None
    ) -> Tuple[str, int]:
        """
        Select the most appropriate SFIA skill and level based on portfolio content
        """
        if suggested_skill and suggested_level:
            return suggested_skill, suggested_level
        
        # Analyze portfolio content to identify skills
        skill_indicators = defaultdict(int)
        complexity_indicators = []
        
        for entry in entries:
            # Extract skill-related keywords and activities
            content_lower = entry.content.lower()
            
            # Common SFIA skill indicators
            if any(word in content_lower for word in ['data', 'database', 'model', 'modelling']):
                skill_indicators['DTAN'] += 1  # Data modelling and design
            if any(word in content_lower for word in ['program', 'code', 'develop', 'software']):
                skill_indicators['PROG'] += 1  # Programming/software development
            if any(word in content_lower for word in ['system', 'analysis', 'requirement']):
                skill_indicators['BUAN'] += 1  # Business analysis
            if any(word in content_lower for word in ['test', 'testing', 'quality']):
                skill_indicators['TEST'] += 1  # Testing
            if any(word in content_lower for word in ['project', 'manage', 'plan']):
                skill_indicators['PRMG'] += 1  # Project management
            
            # Assess complexity level indicators
            if any(phrase in content_lower for phrase in ['complex', 'challenging', 'difficult']):
                complexity_indicators.append(3)
            elif any(phrase in content_lower for phrase in ['routine', 'simple', 'basic']):
                complexity_indicators.append(2)
            else:
                complexity_indicators.append(3)  # Default to level 3
        
        # Select most frequent skill
        if skill_indicators:
            selected_skill = max(skill_indicators.items(), key=lambda x: x[1])[0]
        else:
            selected_skill = 'DTAN'  # Default to Data modelling and design
        
        # Determine level based on complexity and autonomy indicators
        avg_complexity = sum(complexity_indicators) / len(complexity_indicators) if complexity_indicators else 3
        selected_level = max(2, min(4, int(round(avg_complexity))))  # Clamp between 2-4
        
        return selected_skill, selected_level
    
    async def _map_entries_to_skill_components(
        self,
        entries: List[PortfolioEntry],
        skill_code: str,
        skill_level: int
    ) -> List[SkillComponentMapping]:
        """
        Map portfolio entries to SFIA skill components
        """
        # Get skill components from knowledge graph
        skill_data = await self.knowledge_graph.get_skill_details(skill_code, skill_level)
        
        if not skill_data:
            # Fallback for DTAN Level 3 (from the example)
            components = [
                "Applies data analysis, design, modelling, and quality assurance techniques, based upon a detailed understanding of business processes, to establish, modify or maintain data structures and associated components (entity descriptions, relationship descriptions, attribute definitions).",
                "Advises database designers and other application development team members on the details of data structures and associated components."
            ]
        else:
            components = skill_data.get('activities', [skill_data.get('description', '')])
        
        mappings = []
        
        for i, component in enumerate(components):
            mapping = SkillComponentMapping(
                skill_code=skill_code,
                skill_level=skill_level,
                component_description=component,
                portfolio_entries=[],
                coverage_percentage=0.0,
                evidence_quality=EvidenceQuality.ASSERTION_BASED,
                supervisor_verified=False
            )
            
            # Map entries to this component
            relevant_entries = []
            for entry in entries:
                if await self._entry_addresses_component(entry, component):
                    relevant_entries.append(entry.id)
                    mapping.supervisor_verified = mapping.supervisor_verified or entry.supervisor_verified
            
            mapping.portfolio_entries = relevant_entries
            mapping.coverage_percentage = min(100.0, len(relevant_entries) * 50.0)  # Each entry = 50% coverage
            
            # Assess overall evidence quality
            if relevant_entries:
                evidence_qualities = [entry.evidence_quality for entry in entries if entry.id in relevant_entries]
                if any(eq == EvidenceQuality.EVIDENCE_BASED for eq in evidence_qualities):
                    mapping.evidence_quality = EvidenceQuality.EVIDENCE_BASED
                else:
                    mapping.evidence_quality = EvidenceQuality.ASSERTION_BASED
            
            mappings.append(mapping)
        
        return mappings
    
    async def _entry_addresses_component(self, entry: PortfolioEntry, component: str) -> bool:
        """
        Determine if a portfolio entry addresses a specific skill component
        """
        # Simple keyword matching - can be enhanced with NLP
        component_keywords = self._extract_keywords(component.lower())
        entry_keywords = self._extract_keywords(entry.content.lower())
        
        # Check for overlap
        overlap = len(set(component_keywords) & set(entry_keywords))
        return overlap >= 2  # Require at least 2 keyword matches
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        words = re.findall(r'\b\w{3,}\b', text.lower())
        return [word for word in words if word not in stop_words]
    
    async def _assess_technical_achievement(
        self,
        component_mappings: List[SkillComponentMapping],
        supervisor_comments: List[SupervisorComment],
        skill_code: str,
        skill_level: int
    ) -> TechnicalAchievementAssessment:
        """
        Assess technical achievement according to IoC criteria
        """
        assessment = TechnicalAchievementAssessment(
            skill_code=skill_code,
            skill_level=skill_level
        )
        
        # Check items of evidence
        assessment.portfolio_entries_present = len(component_mappings) > 0 and any(
            len(mapping.portfolio_entries) > 0 for mapping in component_mappings
        )
        assessment.supervisor_comments_present = len(supervisor_comments) > 0 and any(
            comment.accuracy_confirmation for comment in supervisor_comments
        )
        
        # Calculate coverage percentages
        if component_mappings:
            # Check 85% threshold
            multiple_entry_components_85 = sum(
                1 for mapping in component_mappings if len(mapping.portfolio_entries) >= 2
            )
            assessment.multiple_entries_85_percent = (
                multiple_entry_components_85 / len(component_mappings)
            ) >= 0.85
            
            # Check 50% threshold
            assessment.multiple_entries_50_percent = (
                multiple_entry_components_85 / len(component_mappings)
            ) >= 0.50
        
        # Check supervisor evaluation context
        assessment.supervisor_evaluates_context = any(
            comment.contextual_evaluation for comment in supervisor_comments
        )
        
        # Check evidence-based entries
        evidence_based_count = sum(
            1 for mapping in component_mappings 
            if mapping.evidence_quality == EvidenceQuality.EVIDENCE_BASED
        )
        assessment.evidence_based_entries = (
            evidence_based_count / len(component_mappings) if component_mappings else 0
        ) >= 0.5
        
        # Calculate scores using IoC methodology
        items_present = int(assessment.portfolio_entries_present) + int(assessment.supervisor_comments_present)
        assessment.items_present_score = items_present
        
        criteria_satisfied = sum([
            assessment.multiple_entries_85_percent,
            assessment.multiple_entries_50_percent,
            assessment.supervisor_evaluates_context,
            assessment.evidence_based_entries
        ])
        assessment.criteria_satisfied_percentage = criteria_satisfied / 4.0
        
        # Apply IoC scoring scheme (Table 1c)
        if items_present == 2:  # All items present
            if assessment.criteria_satisfied_percentage == 1.0:  # 100% criteria
                assessment.unweighted_score = 4
            elif assessment.criteria_satisfied_percentage >= 0.75:  # 75% criteria
                assessment.unweighted_score = 3
            elif assessment.criteria_satisfied_percentage >= 0.50:  # 50% criteria
                assessment.unweighted_score = 2
            else:  # < 50% criteria
                assessment.unweighted_score = 1
        elif items_present == 1:  # 1 item missing
            if assessment.criteria_satisfied_percentage == 1.0:  # 100% criteria
                assessment.unweighted_score = 2
            elif assessment.criteria_satisfied_percentage > 0.50:  # > 50% criteria
                assessment.unweighted_score = 1
            else:
                assessment.unweighted_score = 0
        else:  # 2+ missing or none
            assessment.unweighted_score = 0
        
        return assessment
    
    async def _assess_reflection(
        self,
        entries: List[PortfolioEntry],
        supervisor_comments: List[SupervisorComment]
    ) -> ReflectionAssessment:
        """
        Assess reflection according to IoC criteria
        """
        assessment = ReflectionAssessment()
        
        # Identify reflective entries
        reflective_entries = [
            entry for entry in entries 
            if entry.entry_type == PortfolioEntryType.REFLECTION or len(entry.reflective_elements) > 0
        ]
        
        # Check items of evidence
        assessment.reflective_entries_present = len(reflective_entries) > 0
        
        # Check for personal development identification
        development_indicators = ['learn', 'develop', 'improve', 'growth', 'skill', 'knowledge']
        assessment.personal_development_identified = any(
            any(indicator in entry.content.lower() for indicator in development_indicators)
            for entry in reflective_entries
        )
        
        # Check for professional accountability
        assessment.accountability_demonstrated = any(
            entry.professional_accountability is not None
            for entry in reflective_entries
        )
        
        # Check quality criteria
        assessment.professional_style = all(
            len(entry.content) > 50 and not entry.content.islower()  # Basic professionalism check
            for entry in reflective_entries
        ) if reflective_entries else False
        
        assessment.evidence_based_reflection = any(
            entry.evidence_quality == EvidenceQuality.EVIDENCE_BASED
            for entry in reflective_entries
        )
        
        # Personal development comparison - look for before/after or comparative language
        comparison_indicators = ['before', 'after', 'initially', 'now', 'improved', 'better', 'compared']
        assessment.development_comparison = any(
            any(indicator in entry.content.lower() for indicator in comparison_indicators)
            for entry in reflective_entries
        )
        
        # Customer-facing accountability
        customer_indicators = ['customer', 'client', 'user', 'stakeholder', 'impact', 'important']
        assessment.customer_facing_accountability = any(
            any(indicator in entry.content.lower() for indicator in customer_indicators)
            for entry in reflective_entries
        )
        
        # Calculate scores
        items_present = sum([
            assessment.reflective_entries_present,
            assessment.personal_development_identified,
            assessment.accountability_demonstrated
        ])
        assessment.items_present_score = items_present
        
        criteria_satisfied = sum([
            assessment.professional_style,
            assessment.evidence_based_reflection,
            assessment.development_comparison,
            assessment.customer_facing_accountability
        ])
        assessment.criteria_satisfied_score = criteria_satisfied
        
        # Apply IoC scoring scheme for reflection
        if items_present == 3:  # All items present
            if criteria_satisfied >= 3:  # Most criteria satisfied
                assessment.unweighted_score = 4
            elif criteria_satisfied >= 2:
                assessment.unweighted_score = 3
            elif criteria_satisfied >= 1:
                assessment.unweighted_score = 2
            else:
                assessment.unweighted_score = 1
        elif items_present == 2:  # 1 item missing
            if criteria_satisfied >= 2:
                assessment.unweighted_score = 2
            elif criteria_satisfied >= 1:
                assessment.unweighted_score = 1
            else:
                assessment.unweighted_score = 0
        else:  # 2+ missing or none
            assessment.unweighted_score = max(0, min(2, items_present))
        
        return assessment
    
    async def _assess_generic_responsibility_characteristics(
        self,
        entries: List[PortfolioEntry],
        supervisor_comments: List[SupervisorComment],
        skill_level: int
    ) -> List[GenericResponsibilityAssessment]:
        """
        Assess generic responsibility characteristics
        """
        assessments = []
        
        # Define core characteristics for Level 3 (from IoC example)
        level_3_core_characteristics = [
            GenericResponsibilityCharacteristic.WORKS_UNDER_GENERAL_DIRECTION,
            GenericResponsibilityCharacteristic.USES_DISCRETION_COMPLEX_ISSUES,
            GenericResponsibilityCharacteristic.DETERMINES_ESCALATION,
            GenericResponsibilityCharacteristic.PLANS_MONITORS_WORK,
            GenericResponsibilityCharacteristic.INTERACTS_INFLUENCES_COLLEAGUES,
            GenericResponsibilityCharacteristic.OVERSEES_OTHERS,
            GenericResponsibilityCharacteristic.WORKING_CONTACT_CUSTOMERS,
            GenericResponsibilityCharacteristic.COLLABORATES_USER_NEEDS,
            GenericResponsibilityCharacteristic.CONTRIBUTES_TEAMS,
            GenericResponsibilityCharacteristic.PERFORMS_RANGE_WORK,
            GenericResponsibilityCharacteristic.APPLIES_METHODICAL_APPROACH,
            GenericResponsibilityCharacteristic.APPRECIATION_BUSINESS_CONTEXT,
            GenericResponsibilityCharacteristic.DEMONSTRATES_EFFECTIVE_APPLICATION,
            GenericResponsibilityCharacteristic.TAKES_INITIATIVE_DEVELOPMENT,
            GenericResponsibilityCharacteristic.EFFECTIVE_COMMUNICATION,
            GenericResponsibilityCharacteristic.DEMONSTRATES_JUDGEMENT,
            GenericResponsibilityCharacteristic.IMPACTS_SECURITY_ETHICS
        ]
        
        # All characteristics (including supplementary)
        all_characteristics = list(GenericResponsibilityCharacteristic)
        
        for characteristic in all_characteristics:
            assessment = GenericResponsibilityAssessment(
                characteristic=characteristic,
                is_core=characteristic in level_3_core_characteristics
            )
            
            # Look for evidence in portfolio entries
            evidence_entries = await self._find_evidence_for_characteristic(
                characteristic, entries, supervisor_comments
            )
            
            assessment.evidence_entries = [entry.id for entry in evidence_entries]
            assessment.demonstrated = len(evidence_entries) > 0
            
            if evidence_entries:
                # Assess evidence quality
                evidence_qualities = [entry.evidence_quality for entry in evidence_entries]
                if any(eq == EvidenceQuality.EVIDENCE_BASED for eq in evidence_qualities):
                    assessment.evidence_quality = EvidenceQuality.EVIDENCE_BASED
                else:
                    assessment.evidence_quality = EvidenceQuality.ASSERTION_BASED
            
            assessments.append(assessment)
        
        return assessments
    
    async def _find_evidence_for_characteristic(
        self,
        characteristic: GenericResponsibilityCharacteristic,
        entries: List[PortfolioEntry],
        supervisor_comments: List[SupervisorComment]
    ) -> List[PortfolioEntry]:
        """
        Find portfolio entries that provide evidence for a specific characteristic
        """
        # Define keyword patterns for each characteristic
        characteristic_patterns = {
            GenericResponsibilityCharacteristic.WORKS_UNDER_GENERAL_DIRECTION: 
                ['supervisor', 'direction', 'guidance', 'asked', 'told'],
            GenericResponsibilityCharacteristic.USES_DISCRETION_COMPLEX_ISSUES:
                ['complex', 'challenging', 'difficult', 'decision', 'chose'],
            GenericResponsibilityCharacteristic.DETERMINES_ESCALATION:
                ['escalate', 'ask', 'supervisor', 'help', 'guidance'],
            GenericResponsibilityCharacteristic.PLANS_MONITORS_WORK:
                ['plan', 'schedule', 'monitor', 'deadline', 'timeline'],
            GenericResponsibilityCharacteristic.INTERACTS_INFLUENCES_COLLEAGUES:
                ['team', 'colleague', 'worked with', 'collaborated', 'influenced'],
            GenericResponsibilityCharacteristic.WORKING_CONTACT_CUSTOMERS:
                ['customer', 'client', 'user', 'stakeholder', 'meeting'],
            GenericResponsibilityCharacteristic.CONTRIBUTES_TEAMS:
                ['team', 'group', 'collaborate', 'together', 'contributed'],
            GenericResponsibilityCharacteristic.PERFORMS_RANGE_WORK:
                ['various', 'different', 'range', 'multiple', 'diverse'],
            GenericResponsibilityCharacteristic.APPLIES_METHODICAL_APPROACH:
                ['systematic', 'methodical', 'approach', 'process', 'structured'],
            GenericResponsibilityCharacteristic.APPRECIATION_BUSINESS_CONTEXT:
                ['business', 'company', 'organization', 'impact', 'important'],
            GenericResponsibilityCharacteristic.EFFECTIVE_COMMUNICATION:
                ['communicate', 'explained', 'presented', 'discussed', 'meeting'],
            GenericResponsibilityCharacteristic.TAKES_INITIATIVE_DEVELOPMENT:
                ['learn', 'developed', 'training', 'course', 'skill']
        }
        
        patterns = characteristic_patterns.get(characteristic, [])
        evidence_entries = []
        
        for entry in entries:
            content_lower = entry.content.lower()
            if any(pattern in content_lower for pattern in patterns):
                evidence_entries.append(entry)
        
        return evidence_entries
    
    async def _evaluate_generic_responsibility_thresholds(
        self,
        assessments: List[GenericResponsibilityAssessment]
    ) -> bool:
        """
        Evaluate generic responsibility thresholds according to IoC methodology
        """
        core_assessments = [a for a in assessments if a.is_core]
        
        # Count demonstrated core characteristics
        core_demonstrated = sum(1 for a in core_assessments if a.demonstrated)
        
        # Count total instances of core characteristics
        core_instances = sum(len(a.evidence_entries) for a in core_assessments)
        
        # Count total instances of all characteristics
        total_instances = sum(len(a.evidence_entries) for a in assessments)
        
        # Check thresholds
        threshold_1 = core_demonstrated >= self.CORE_CHARACTERISTICS_THRESHOLD
        threshold_2 = core_instances >= self.CORE_INSTANCES_THRESHOLD
        threshold_3 = total_instances >= self.TOTAL_INSTANCES_THRESHOLD
        
        return threshold_1 and threshold_2 and threshold_3
    
    def _determine_proficiency_threshold(self, total_score: float) -> ProficiencyThreshold:
        """Determine proficiency threshold based on total score"""
        if total_score >= self.COMPETENCY_THRESHOLD:
            return ProficiencyThreshold.COMPETENCY
        elif total_score >= self.PROFICIENCY_THRESHOLD:
            return ProficiencyThreshold.PROFICIENCY
        else:
            return ProficiencyThreshold.DEVELOPING
    
    async def _assess_evidence_quality(self, content: str) -> EvidenceQuality:
        """Assess the quality of evidence in portfolio entry content"""
        # Look for specific evidence indicators
        evidence_indicators = [
            'number of', 'cardinality', 'classes', 'entity types', 'tables',
            'specific', 'detailed', 'example', 'instance', 'particular',
            'discovered', 'found', 'identified', 'analyzed', 'compared'
        ]
        
        content_lower = content.lower()
        evidence_count = sum(1 for indicator in evidence_indicators if indicator in content_lower)
        
        # Also check for vague assertion words
        assertion_indicators = ['I think', 'I believe', 'probably', 'maybe', 'should be']
        assertion_count = sum(1 for indicator in assertion_indicators if indicator in content_lower)
        
        if evidence_count >= 2 and assertion_count == 0:
            return EvidenceQuality.EVIDENCE_BASED
        elif evidence_count >= 1:
            return EvidenceQuality.ASSERTION_BASED
        else:
            return EvidenceQuality.INSUFFICIENT
    
    async def _extract_reflective_elements(self, content: str) -> List[str]:
        """Extract reflective elements from portfolio entry content"""
        reflective_patterns = [
            r"I (?:realized|discovered|learned|understood|found)",
            r"(?:This|It) (?:taught|showed|demonstrated)",
            r"Looking back",
            r"In retrospect",
            r"I would (?:do|approach|handle)",
            r"Next time"
        ]
        
        reflective_elements = []
        content_lower = content.lower()
        
        for pattern in reflective_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            reflective_elements.extend(matches)
        
        return reflective_elements
    
    async def _identify_professional_accountability(self, content: str) -> Optional[str]:
        """Identify evidence of professional accountability"""
        accountability_indicators = [
            'important to the company',
            'customer impact',
            'business critical',
            'stakeholder',
            'responsible for',
            'accountable',
            'my role was crucial'
        ]
        
        content_lower = content.lower()
        for indicator in accountability_indicators:
            if indicator in content_lower:
                # Extract the sentence containing the indicator
                sentences = content.split('.')
                for sentence in sentences:
                    if indicator in sentence.lower():
                        return sentence.strip()
        
        return None
    
    async def _get_skill_name(self, skill_code: str) -> str:
        """Get skill name from knowledge graph"""
        try:
            skill_data = await self.knowledge_graph.get_skill_details(skill_code)
            return skill_data.get('name', skill_code) if skill_data else skill_code
        except:
            # Fallback skill names
            skill_names = {
                'DTAN': 'Data modelling and design',
                'PROG': 'Programming/software development',
                'BUAN': 'Business analysis',
                'TEST': 'Testing',
                'PRMG': 'Project management'
            }
            return skill_names.get(skill_code, skill_code)
    
    async def _generate_recommendations(self, assessment: PortfolioAssessment) -> List[str]:
        """Generate recommendations based on assessment results"""
        recommendations = []
        
        # Technical achievement recommendations
        if assessment.technical_achievement.unweighted_score < 3:
            if not assessment.technical_achievement.multiple_entries_85_percent:
                recommendations.append(
                    "Increase portfolio entries coverage: Ensure at least 85% of skill components have multiple entries"
                )
            
            if not assessment.technical_achievement.evidence_based_entries:
                recommendations.append(
                    "Improve evidence quality: Include specific details, numbers, and concrete examples rather than general assertions"
                )
            
            if not assessment.technical_achievement.supervisor_evaluates_context:
                recommendations.append(
                    "Request supervisor to provide contextual evaluation of achievements and their difficulty"
                )
        
        # Reflection recommendations
        if assessment.reflection_assessment.unweighted_score < 3:
            if not assessment.reflection_assessment.personal_development_identified:
                recommendations.append(
                    "Enhance reflection: Clearly identify personal development areas and learning outcomes"
                )
            
            if not assessment.reflection_assessment.development_comparison:
                recommendations.append(
                    "Add comparative reflection: Include before/after comparisons showing skill development progression"
                )
            
            if not assessment.reflection_assessment.customer_facing_accountability:
                recommendations.append(
                    "Demonstrate accountability: Include reflection on customer/business impact and professional responsibility"
                )
        
        # Generic responsibility recommendations
        if not assessment.generic_responsibility_pass:
            core_demonstrated = sum(
                1 for a in assessment.generic_responsibility_assessments 
                if a.is_core and a.demonstrated
            )
            
            if core_demonstrated < self.CORE_CHARACTERISTICS_THRESHOLD:
                recommendations.append(
                    f"Increase core characteristic evidence: Currently {core_demonstrated}/{len([a for a in assessment.generic_responsibility_assessments if a.is_core])} core characteristics demonstrated"
                )
        
        # Overall recommendations
        if assessment.proficiency_threshold == ProficiencyThreshold.DEVELOPING:
            recommendations.append(
                f"Overall score improvement needed: Current score {assessment.total_weighted_score:.1f}, need 65+ for proficiency"
            )
        
        return recommendations
    
    async def get_portfolio_mapping_guidance(
        self,
        activities_description: str,
        student_level: str = "placement"
    ) -> PortfolioMappingGuidance:
        """
        Provide guidance for mapping portfolio activities to SFIA skills
        """
        # Analyze activities to suggest appropriate SFIA skills
        recommended_skills = await self._suggest_sfia_skills(activities_description)
        
        # Generate mapping suggestions
        mapping_suggestions = await self._generate_mapping_suggestions(activities_description)
        
        # Provide evidence requirements
        evidence_requirements = {
            "technical_achievement": {
                "multiple_entries_per_component": "At least 85% of skill components need multiple portfolio entries",
                "supervisor_verification": "Supervisor comments confirming accuracy of entries",
                "evidence_based_content": "Entries should contain specific details and examples",
                "contextual_evaluation": "Supervisor should evaluate achievements against their context"
            },
            "reflection": {
                "reflective_entries": "Include reflective portfolio entries across the skill area",
                "personal_development": "Identify areas of personal development",
                "professional_accountability": "Demonstrate understanding of professional accountability",
                "evidence_based_reflection": "Base reflection on evidence rather than assertion"
            }
        }
        
        # Quality criteria
        quality_criteria = [
            "Portfolio entries should be based on evidence rather than assertion",
            "Include specific details like numbers, quantities, and concrete examples", 
            "Demonstrate the challenges encountered and how they were overcome",
            "Show progression and development over time",
            "Include supervisor verification and contextual comments",
            "Reflect on business impact and professional accountability"
        ]
        
        # Best practices
        best_practices = [
            "Document separate achievements rather than incremental progress on the same task",
            "Include variety in types of evidence and activities",
            "Ensure professional writing style throughout",
            "Provide sufficient detail to demonstrate competency without being verbose",
            "Connect activities to broader business context and objectives",
            "Include both technical and soft skill demonstrations"
        ]
        
        return PortfolioMappingGuidance(
            recommended_skills=recommended_skills,
            mapping_suggestions=mapping_suggestions,
            evidence_requirements=evidence_requirements,
            quality_criteria=quality_criteria,
            best_practices=best_practices
        )
    
    async def _suggest_sfia_skills(self, activities: str) -> List[Dict[str, Any]]:
        """Suggest appropriate SFIA skills based on activity description"""
        suggestions = []
        activities_lower = activities.lower()
        
        skill_patterns = {
            'DTAN': {
                'name': 'Data modelling and design',
                'keywords': ['data', 'database', 'model', 'entity', 'relationship', 'structure'],
                'level_indicators': {
                    2: ['simple', 'basic', 'guided'],
                    3: ['complex', 'detailed', 'business process', 'quality assurance'],
                    4: ['strategic', 'enterprise', 'architectural']
                }
            },
            'PROG': {
                'name': 'Programming/software development',
                'keywords': ['program', 'code', 'develop', 'software', 'application'],
                'level_indicators': {
                    2: ['simple', 'basic', 'scripts'],
                    3: ['complex', 'systems', 'integration'],
                    4: ['architecture', 'frameworks', 'standards']
                }
            },
            'BUAN': {
                'name': 'Business analysis',
                'keywords': ['requirements', 'analysis', 'business', 'stakeholder', 'process'],
                'level_indicators': {
                    2: ['gather', 'document', 'simple'],
                    3: ['analyze', 'complex', 'solutions'],
                    4: ['strategic', 'organizational', 'transformation']
                }
            }
        }
        
        for skill_code, skill_info in skill_patterns.items():
            keyword_matches = sum(1 for keyword in skill_info['keywords'] if keyword in activities_lower)
            
            if keyword_matches >= 2:  # At least 2 keyword matches
                # Determine suggested level
                suggested_level = 3  # Default
                for level, indicators in skill_info['level_indicators'].items():
                    if any(indicator in activities_lower for indicator in indicators):
                        suggested_level = level
                        break
                
                suggestions.append({
                    'skill_code': skill_code,
                    'skill_name': skill_info['name'],
                    'suggested_level': suggested_level,
                    'confidence': min(1.0, keyword_matches / len(skill_info['keywords'])),
                    'matching_keywords': [kw for kw in skill_info['keywords'] if kw in activities_lower]
                })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:3]  # Return top 3
    
    async def _generate_mapping_suggestions(self, activities: str) -> List[Dict[str, Any]]:
        """Generate specific mapping suggestions"""
        suggestions = [
            {
                'type': 'entry_coverage',
                'title': 'Ensure Multiple Entries per Component',
                'description': 'Each SFIA skill component should be addressed by multiple portfolio entries showing different instances of the same type of activity.',
                'example': 'If assessing data modelling, include entries for different databases or data structures you worked with.'
            },
            {
                'type': 'evidence_quality',
                'title': 'Include Specific Evidence',
                'description': 'Provide concrete details such as numbers of entities, table cardinalities, or specific challenges encountered.',
                'example': 'Instead of "I designed a database", write "I designed a customer database with 8 entity types and resolved 3 data integrity issues".'
            },
            {
                'type': 'supervisor_input',
                'title': 'Obtain Supervisor Verification',
                'description': 'Ensure your workplace supervisor provides comments confirming the accuracy and context of your achievements.',
                'example': 'Supervisor should comment on the difficulty level and importance of your contributions to the organization.'
            }
        ]
        
        return suggestions