# SPARQL Queries for Enhanced SFIA 9 Ontology

This document provides practical SPARQL queries for analyzing the enhanced SFIA 9 ontology, including professional roles, competency profiles, and career pathways.

## Prerequisites
```sparql
PREFIX sfia: <https://rdf.sfia-online.org/9/ontology/>
PREFIX skills: <https://rdf.sfia-online.org/9/skills/>
PREFIX skilllevels: <https://rdf.sfia-online.org/9/skilllevels/>
PREFIX levels: <https://rdf.sfia-online.org/9/lor/>
PREFIX categories: <https://rdf.sfia-online.org/9/categories/>
PREFIX roles: <https://rdf.sfia-online.org/9/roles/>
PREFIX profiles: <https://rdf.sfia-online.org/9/profiles/>
PREFIX pathways: <https://rdf.sfia-online.org/9/pathways/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
```

## 1. Basic Skills Analysis

### Find all skills in a specific category
```sparql
SELECT ?skill ?skillName ?level ?levelDescription
WHERE {
    ?skill a sfia:Skill ;
           rdfs:label ?skillName ;
           sfia:skillCategory categories:strategy_and_planning ;
           sfia:definedAtLevel ?skillLevel .
    ?skillLevel sfia:level ?level ;
                sfia:skillLevelDescription ?levelDescription .
}
ORDER BY ?skillName ?level
```

### Skills prerequisite chain
```sparql
SELECT ?skill ?fromLevel ?toLevel
WHERE {
    ?fromSkillLevel sfia:prerequisiteFor ?toSkillLevel .
    ?fromSkillLevel sfia:skill ?skill ; sfia:level ?fromLevel .
    ?toSkillLevel sfia:skill ?skill ; sfia:level ?toLevel .
}
ORDER BY ?skill ?fromLevel
```

## 2. Professional Role Analysis

### Role skill requirements
```sparql
SELECT ?role ?roleName ?skill ?skillName ?level ?priority
WHERE {
    ?role a sfia:ProfessionalRole ;
          rdfs:label ?roleName .
    
    # Essential skills
    {
        ?role sfia:requiresEssentialSkill ?skillLevel .
        BIND("essential" AS ?priority)
    }
    UNION
    # Desirable skills  
    {
        ?role sfia:requiresDesirableSkill ?skillLevel .
        BIND("desirable" AS ?priority)
    }
    
    ?skillLevel sfia:skill ?skill ; sfia:level ?level .
    ?skill rdfs:label ?skillName .
}
ORDER BY ?roleName ?priority ?skillName
```

### Roles by complexity (number of required skills)
```sparql
SELECT ?role ?roleName (COUNT(?skillLevel) AS ?skillCount)
WHERE {
    ?role a sfia:ProfessionalRole ;
          rdfs:label ?roleName ;
          sfia:requiresEssentialSkill ?skillLevel .
}
GROUP BY ?role ?roleName
ORDER BY DESC(?skillCount)
```

## 3. Career Pathway Analysis

### Direct career progressions
```sparql
SELECT ?fromRole ?fromRoleName ?toRole ?toRoleName ?additionalSkills
WHERE {
    ?pathway a sfia:CareerPathway ;
             sfia:fromRole ?fromRole ;
             sfia:toRole ?toRole .
    
    ?fromRole rdfs:label ?fromRoleName .
    ?toRole rdfs:label ?toRoleName .
    
    OPTIONAL {
        ?pathway sfia:requiresAdditionalSkill ?addSkill .
        ?addSkill rdfs:label ?additionalSkills .
    }
}
ORDER BY ?fromRoleName ?toRoleName
```

### Multi-step career paths (using property paths)
```sparql
SELECT ?startRole ?startRoleName ?endRole ?endRoleName
WHERE {
    ?startRole sfia:progressesTo+ ?endRole .
    ?startRole rdfs:label ?startRoleName .
    ?endRole rdfs:label ?endRoleName .
    
    # Exclude direct progressions (we want multi-step)
    FILTER NOT EXISTS { ?startRole sfia:progressesTo ?endRole }
}
ORDER BY ?startRoleName ?endRoleName
```

## 4. Skill Gap Analysis

### Skills gap for a specific role transition
```sparql
SELECT ?skill ?skillName ?requiredLevel ?currentLevel (?requiredLevel - ?currentLevel AS ?gap)
WHERE {
    # Target role requirements
    roles:SWARCH sfia:requiresEssentialSkill ?targetSkillLevel .
    ?targetSkillLevel sfia:skill ?skill ; sfia:level ?requiredLevel .
    
    # Current role capabilities
    roles:DEVLEAD sfia:requiresEssentialSkill ?currentSkillLevel .
    ?currentSkillLevel sfia:skill ?skill ; sfia:level ?currentLevel .
    
    ?skill rdfs:label ?skillName .
    
    # Only show gaps (where target level is higher)
    FILTER(?requiredLevel > ?currentLevel)
}
ORDER BY DESC(?gap) ?skillName
```

### Missing skills for role transition
```sparql
SELECT ?skill ?skillName ?requiredLevel
WHERE {
    # Skills required by target role
    roles:SWARCH sfia:requiresEssentialSkill ?skillLevel .
    ?skillLevel sfia:skill ?skill ; sfia:level ?requiredLevel .
    ?skill rdfs:label ?skillName .
    
    # Skills NOT present in current role
    FILTER NOT EXISTS {
        roles:DEVLEAD sfia:requiresEssentialSkill ?currentSkillLevel .
        ?currentSkillLevel sfia:skill ?skill .
    }
}
ORDER BY ?skillName
```

## 5. Competency Profile Analysis

### Profile skill distribution by priority
```sparql
SELECT ?profile ?profileName ?priority (COUNT(?skill) AS ?skillCount)
WHERE {
    ?profile a sfia:CompetencyProfile ;
             rdfs:label ?profileName ;
             sfia:hasRequirement ?req .
    
    ?req sfia:requiresSkillLevel ?skillLevel ;
         sfia:priority ?priority .
    ?skillLevel sfia:skill ?skill .
}
GROUP BY ?profile ?profileName ?priority
ORDER BY ?profileName ?priority
```

### Overlapping skills between profiles
```sparql
SELECT ?profile1 ?profile1Name ?profile2 ?profile2Name ?skill ?skillName
WHERE {
    ?profile1 sfia:hasRequirement/sfia:requiresSkillLevel/sfia:skill ?skill .
    ?profile2 sfia:hasRequirement/sfia:requiresSkillLevel/sfia:skill ?skill .
    
    ?profile1 rdfs:label ?profile1Name .
    ?profile2 rdfs:label ?profile2Name .
    ?skill rdfs:label ?skillName .
    
    FILTER(?profile1 < ?profile2)  # Avoid duplicates
}
ORDER BY ?profile1Name ?profile2Name ?skillName
```

## 6. Advanced Analytics

### Skills centrality (most commonly required across roles)
```sparql
SELECT ?skill ?skillName (COUNT(DISTINCT ?role) AS ?roleCount)
WHERE {
    ?role a sfia:ProfessionalRole ;
          sfia:requiresEssentialSkill ?skillLevel .
    ?skillLevel sfia:skill ?skill .
    ?skill rdfs:label ?skillName .
}
GROUP BY ?skill ?skillName
ORDER BY DESC(?roleCount)
```

### Level distribution across skills
```sparql
SELECT ?level (COUNT(DISTINCT ?skill) AS ?skillCount) 
       (COUNT(DISTINCT ?skillLevel) AS ?skillLevelCount)
WHERE {
    ?skillLevel sfia:level ?level ;
                sfia:skill ?skill .
}
GROUP BY ?level
ORDER BY ?level
```

### Category breadth analysis
```sparql
SELECT ?category ?categoryName (COUNT(DISTINCT ?skill) AS ?skillCount)
WHERE {
    ?skill sfia:skillCategory ?category .
    ?category skos:prefLabel ?categoryName .
}
GROUP BY ?category ?categoryName
ORDER BY DESC(?skillCount)
```

## 7. Validation and Quality Queries

### Find skills without level definitions
```sparql
SELECT ?skill ?skillName
WHERE {
    ?skill a sfia:Skill ;
           rdfs:label ?skillName .
    FILTER NOT EXISTS { ?skill sfia:definedAtLevel ?level }
}
```

### Find roles without skill requirements
```sparql
SELECT ?role ?roleName
WHERE {
    ?role a sfia:ProfessionalRole ;
          rdfs:label ?roleName .
    FILTER NOT EXISTS { 
        ?role sfia:requiresEssentialSkill|sfia:requiresDesirableSkill ?skill 
    }
}
```

### Check for circular career progressions
```sparql
SELECT ?role1 ?role2
WHERE {
    ?role1 sfia:progressesTo+ ?role2 .
    ?role2 sfia:progressesTo+ ?role1 .
    FILTER(?role1 != ?role2)
}
```

## 8. Reporting Queries

### Executive summary statistics
```sparql
SELECT 
    (COUNT(DISTINCT ?skill) AS ?totalSkills)
    (COUNT(DISTINCT ?role) AS ?totalRoles)
    (COUNT(DISTINCT ?pathway) AS ?totalPathways)
    (COUNT(DISTINCT ?category) AS ?totalCategories)
WHERE {
    OPTIONAL { ?skill a sfia:Skill }
    OPTIONAL { ?role a sfia:ProfessionalRole }
    OPTIONAL { ?pathway a sfia:CareerPathway }
    OPTIONAL { ?category a sfia:Category }
}
```

### Skills maturity matrix
```sparql
SELECT ?skill ?skillName ?minLevel ?maxLevel (?maxLevel - ?minLevel + 1 AS ?levelRange)
WHERE {
    ?skill a sfia:Skill ;
           rdfs:label ?skillName ;
           sfia:definedAtLevel ?skillLevel .
    ?skillLevel sfia:level ?level .
    
    {
        SELECT ?skill (MIN(?level) AS ?minLevel) (MAX(?level) AS ?maxLevel)
        WHERE {
            ?skill sfia:definedAtLevel ?skillLevel .
            ?skillLevel sfia:level ?level .
        }
        GROUP BY ?skill
    }
}
ORDER BY ?skillName
```