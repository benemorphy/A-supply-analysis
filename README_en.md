# A-supply-analysis

Supply Chain Research Methodology & Toolkit — Conduct cross-domain supply chain deep research through GA

## Positioning

A-supply-analysis is not a single-industry data analysis system. It provides **a complete methodology + toolkit framework**:

- **Methodology**: A 3-layer deep research workflow (target selection → breadth search → depth mining → intelligent analysis)
- **Toolkit**: 8 RESTful API endpoints + LLM cleaning pipeline + Graph database + Visualization + Ontology reasoning
- **Gateway**: Users initiate research through GA, which drives this toolkit through the full workflow, and returns analysis results to the user

## Research Workflow

```
User initiates research via GA
        |
        v
  1. Select domain + target companies  <--  LLM recommendation + user confirmation
  2. Multi-source search + LLM extraction  <--  metaso search + de-anonymization
  3. Data ingestion  <--  REST API push + auto-dedup
  4. Graph analysis + path propagation  <--  Neo4j graph database
  5. Risk assessment  <--  dependency calculation + critical node identification
  6. Deep research  <--  Layer 1-3 pipeline
  7. Report delivery  <--  LLM panoramic analysis report
        |
        v
  User receives research results
```

## Toolkit Capabilities

| Capability | Description | API |
|------------|-------------|:---:|
| Company management | Add/list target companies | `GET/POST /api/companies` |
| Relation management | Push/query supply relations | `GET/POST /api/supply-chains` |
| LLM cleaning | Filter anonymous names | `POST /api/clean` |
| Risk analysis | Single dependency + critical nodes | `GET /api/risk-analysis` |
| Analysis report | LLM-generated report | `GET /api/report` |
| Graph JSON | D3 force-directed data | `GET /api/visualize` |
| Visualization | Interactive D3 page | `GET /api/graph-view` |
| Deep research | 3-layer search+analysis pipeline | `deep_research/layer1-3.py` |
| OWL ontology | Domain concept modeling + reasoning | `ontology/build_ontology.py` |
| Neo4j import | Graph DB path analysis | `db/neo4j_import.py` |

## Demo

The project comes with **NEV (New Energy Vehicle)** supply chain demo data (7 companies) to verify the toolkit's workflow completeness. Users can repeat this process in any domain.

## Integration

```
+---------+  initiate research  +--------+  drive toolkit  +------------------+
|  User   | ------------------> |   GA   | -------------> | A-supply-analysis |
+---------+                     +--------+                | (REST API :8765)  |
      ^                            |                      +------------------+
      |   deliver results          |                             |
      +----------------------------+                      +------+-------+
                                                            | Neo4j | D3  |
                                                            | LLM   | OWL |
                                                            +-------------+
```
