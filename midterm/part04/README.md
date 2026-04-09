# Midterm Part 4 — Distributed SQL Database Presentation

**ISM 6562 - Big Data for Business Applications**

The fourth and final part of the midterm. Each team picks **one** distributed SQL database from the list of 9 options and presents a deep technical evaluation to the class. This is the part of the midterm where you survey what's beyond manual sharding and Cassandra: production-grade distributed SQL systems that automate sharding, replication, and rebalancing transparently.

## What's in this folder

```
part04/
├── README.md
└── ism6562-midterm-part04.html        # full assignment instructions and the list of systems
```

This part is **research and presentation only** — there is no Docker environment to spin up. Each team produces a 12-15 minute presentation evaluating their chosen system against PostgreSQL (Parts 1-2) and Cassandra (Part 3).

## Reading the assignment

Open `ism6562-midterm-part04.html`. The full assignment covers:

- The 9 distributed SQL systems available for selection (Citus, CockroachDB, YugabyteDB, TiDB, FoundationDB, Fauna, OceanBase, Apache Ignite, SingleStore)
- Selection rules (one team per system, first-come-first-served on Canvas)
- The required evaluation criteria (CAP positioning, consistency model, SQL compatibility, sharding strategy, failure modes, your recommendation)
- Presentation format and grading rubric

## What to submit

- Team presentation slide deck (PDF)
- Each team member must speak during the presentation
- Q&A from the instructor and classmates after each presentation

See the assignment HTML for full details and the grading rubric.

## Why this part matters

After spending Parts 1-3 building polyglot persistence by hand, Part 4 surveys the systems that aim to remove that complexity. Understanding the trade-offs each one makes — and why none of them are a magic bullet — is essential for making informed technology decisions in real data-engineering work. The systems on this list are also part of the broader conversation about *scaling the database paradigm* that we'll contrast against the unbundled big-data approach in Weeks 8-11.
