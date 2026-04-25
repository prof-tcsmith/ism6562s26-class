# Final Project

Materials for the ISM 6562 final project: ten scenarios, one per team.

## Project brief

Open [`ism6562-final-project.html`](ism6562-final-project.html) for the full brief — goals, requirements, stages, rubric, academic-integrity policy, and team logistics. Read this first.

## Scenarios

Each scenario is a fictional company with its own data sources, business questions, and stage scaffolding. Click the project name to read its full description.

| # | Project | Industry | Core challenge |
|---|---------|----------|----------------|
| 01 | [SmartGrid Energy — VoltEdge Power](projects/01-smartgrid-energy/scenario.html) | Utilities / Energy | Real-time grid load balancing and outage prediction |
| 02 | [CityTransit Mobility — MetroLink Transit](projects/02-citytransit-mobility/scenario.html) | Transportation | Route optimization and ridership forecasting |
| 03 | [AgriFlow Farming](projects/03-agriflow-farming/scenario.html) | Agriculture | Crop yield prediction and irrigation optimization |
| 04 | [MediStream Telehealth](projects/04-medistream-telehealth/scenario.html) | Healthcare / Telehealth | Remote patient monitoring and appointment analytics |
| 05 | [FinPulse Fraud](projects/05-finpulse-fraud/scenario.html) | Financial Services | Transaction fraud detection and risk scoring |
| 06 | [CampusIQ University](projects/06-campusiq-university/scenario.html) | Higher Education | Student success prediction and resource optimization |
| 07 | [Sportlytics Athletics](projects/07-sportlytics-athletics/scenario.html) | Sports Analytics | Player performance tracking and injury prediction |
| 08 | [SupplyChain Manufacturing — PrecisionParts](projects/08-supplychain-manufacturing/scenario.html) | Manufacturing / Logistics | Inventory optimization and defect prediction |
| 09 | [ClimaSense Environment](projects/09-climasense-environment/scenario.html) | Environmental Science | Air quality monitoring and pollution forecasting |
| 10 | [MediaWave Streaming](projects/10-mediawave-streaming/scenario.html) | Media / Entertainment | Content recommendation and viewer engagement analytics |

## Repository layout

```
final-projects/
├── README.md
├── ism6562-final-project.html      ← master brief (read first)
├── projects/
│   ├── 01-smartgrid-energy/scenario.html
│   ├── 02-citytransit-mobility/scenario.html
│   ├── ...
│   └── 10-mediawave-streaming/scenario.html
└── data/
    ├── 01-smartgrid-energy/
    ├── 02-citytransit-mobility/
    ├── 03-agriflow-farming/
    ├── 04-medistream-telehealth/
    ├── 05-finpulse-fraud/
    ├── 06-campusiq-university/
    ├── 07-sportlytics-athletics/
    ├── 08-supplychain-manufacturing/
    ├── 09-climasense-environment/
    └── 10-mediawave-streaming/
```

## Accessing the data

From a notebook running inside your lab's Docker network, prefer cloning this repo to get the data locally, or stream files over HTTP via the raw GitHub URL:

```
https://raw.githubusercontent.com/prof-tcsmith/ism6562s26-class/main/final-projects/data/<project-slug>/<file>
```

Milestone deadlines, team assignments, and submission links are posted on Canvas.
