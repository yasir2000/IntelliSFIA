# SFIA 9 in RDF

The SFIA 9 distribution is composed of 3 files:

- Attributes
- Levels of Responsibilities
- Skills

**Note**: the Attributes file also contains the values that each attribute acquires at each level.

Let us see an example of the data converted in RDF (Turtle serialisation format).
Then, we will describe our modelling choices.

```
@prefix attributes: <https://sfia-online.org/en/shortcode/9/> .
@prefix levels: <https://sfia-online.org/en/lor/9/> .
@prefix skills: <https://sfia-online.org/en/skillcode/9/> .
@prefix sfia: <https://sfia-online.org/ontology/> .

# Property (attribute) definition
attributes:AUTO a owl:AnnotationProperty ;
    rdfs:label "Autonomy"@en ;
    rdfs:comment "The level of independence, [..]."@en ;
    skos:notation "AUTO" ;
    sfia:attributeGuidanceNotes "...."@en ;
    sfia:attributeType "Attributes"@en .

# Level of Responsibility
levels:2 a sfia:Level;
    skos:inScheme sfia:LorScheme ;
    skos:notation 1 ;
    attributes:ADAP "Adjusts to different team dynamics ..[..]"@en ;
    attributes:AUTO "Works under routine direction [..]"@en ;
    # (other attributes...)
    sfia:levelEssence "Provides assistance to others, [..]"@en ;
    sfia:levelGuidingPhrase "Assist"@en .

# Skill definition
skills:ITSP a :Skill;
    rdfs:label "Strategic planning"@en ;
    skos:notation "ITSP" ;
    sfia:definedAtLevel <https://sfia-online.org/ontology/skilllevel/ITSP_4>,
        <https://sfia-online.org/ontology/skilllevel/ITSP_5>,
        <https://sfia-online.org/ontology/skilllevel/ITSP_6>,
        <https://sfia-online.org/ontology/skilllevel/ITSP_7> ;
    sfia:skillCategory <https://sfia-online.org/ontology/categories/strategy_and_planning> ;
    sfia:skillDescription "Creating and maintaining organisational-level strategies to align overall business plans, actions and resources with high-level business objectives."@en ;
    sfia:skillNotes ".. focused on enterprise-wide strategic planning and management, [..]"@en .


# Skill level
<https://sfia-online.org/ontology/skilllevel/ITSP_4> a :SkillLevel;
    skos:notation "ITSP_4" ;
    sfia:skillLevel levels:4 ;
    sfia:skillLevelDescription "Contributes to the collection and analysis of information [..]"@en .
```

## Skills and Levels

In SFIA, there are 7 abstract Levels, each representing a concept of ability and autonomy.
No person is a "level X" in general, but always in relation to a skill.
I may be level 1 in one skill and level 7 in another. However, these 7 levels constitute an abstract vocabulary
of their own, that we modelled as a "flat" (1-level only) SKOS concept scheme.
SFIA provides general descriptions for each of them.
SFIA provides resolvable URLs for the levels, for ex. `https://sfia-online.org/en/lor/9/1`.

In SFIA, Skills are generic skills, such as "Strategic planning" (code `ITSP`).
In RDF, we treat `Skill` as a class of objects (the various skills).
We introduce the class `SkillLevel`, whose instances are skills at particular levels. For example,
a person `Johanna` might have, at a given point in her life, `ITSP_5`, that is, a level 5 in Strategic planning.
SFIA provides descriptions and notes both for general skills (ex. `ITSP`) and their embodiment at a level
(ex. `ITSP_4`).
SFIA provides resolvable URLs for the skills, for ex. `https://sfia-online.org/en/skillcode/9/ITSP`.

Skills' _categories_ are given by SFIA to permit to group skills under topics, for ease of classification,
retrievability or navigation. They constitute a mini-taxonomy of their own, so we decided to model them
as a (small) SKOS concept scheme, `sfia:CategoryScheme`. In the current SFIA release,
this scheme has 6 top-level categories, with several sub-categories under them. For example:

```
<https://sfia-online.org/ontology/categories/development_and_implementation> a sfia:Category ;
    skos:inScheme sfia:CategoryScheme ;
    skos:prefLabel "Development and implementation"@en .

<https://sfia-online.org/ontology/categories/user_centred_design> a sfia:Category ;
    skos:broader <https://sfia-online.org/ontology/categories/development_and_implementation> ;
    skos:inScheme sfia:CategoryScheme ;
    skos:prefLabel "User centred design"@en .
```

We see here that "User centred design" is a sub-category of the broader category "Development and implementation".

## Attributes

Attributes are used by SFIA to describe the 7 Levels in detail.
Each level has a general description (the "essence" of the level) but also a description under several dimensions
(adaptability, autonomy, influence, knowledge, etc.) describing what it means to be adaptable, autonomous,
influential, etc., _at that level_.

When converting to RDF, we decided to render Attributes as properties on the Levels of responsibilities.
SFIA provides general descriptions for them.
An alternative decision could have been to make them objects (nodes), but that would have made the model heavier,
without a clear advantage in terms of Knowledge Representation.

SFIA provides resolvable URLs for attributes, for ex. `https://sfia-online.org/en/shortcode/9/AUTO`.

## The conversion script

For ease of maintainability, the core of our script lies in three small parsers (in the `/parsers` folder),
one for each SFIA sheet file.
Each parser returns a set of triples that are then joined, together with some general definitions,
in `convert_sfia.py`.

So, parsing the Attributes file will provide an RDF graph describing the properties for the various Levels.
The resulting RDF graph will then populate the general properties' definitions, and their descriptions at a given Level.
Parsing the Levels file will provide an RDF graph describing the levels.

## Linked Data

This conversion is meant to produce an RDF distribution for a given SFIA 9 published release.
When available, we used SFIA's provided URLs for its entities (levels, skills, attributes..) as IRIs in RDF.
This does not mean that those URLs will provide content-negotiated RDF when visited. They serve useful, well-presented
human-readable HTML. The SFIA initiative is not committed, for now, to serve RDF content, so our contribution here
has been to provide an RDF conversion with what _we think_ is a good trade-off between semantic best practices
and pragmatism.
We give here a summary of the IRI schemes used. As mentioned, when available they come from SFIA, and when not, we
minted our own.
We used `camelCase` naming conventions except for categories, where we "hash" the category name with underscores.

- For Skills: `https://sfia-online.org/en/skillcode/9/_<skill_code>_`
- For Attributes: `https://sfia-online.org/en/shortcode/9/_<attribute_code>_`
- For levels: `https://sfia-online.org/en/lor/9/_<level>_`
- For other properties and classes: `https://sfia-online.org/ontology/`
    - ex. categories: `https://sfia-online.org/ontology/categories/user_centred_design`
    - ex. skill levels: `https://sfia-online.org/ontology/skilllevel/ACIN_2`
    - ex. other property: `https://sfia-online.org/ontology/skillDescription`
