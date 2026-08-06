# RAG Pipeline Quality & Recovery Demo

This interactive demo presents side-by-side evidence comparing RAG behavior across **Baseline Clean**, **Intentionally Corrupted**, and **Raw Lineage Repaired** states.

## 1. Overall Metrics Summary

| Metric | Baseline | Corrupted | Repaired | $\Delta$ (Corrupted - Baseline) | Recovery |
| --- | ---: | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1.0000 | 0.5000 | 1.0000 | -0.5000 | Recovered |
| `mean_token_f1` | 0.8306 | 0.4157 | 0.8306 | -0.4148 | Recovered |
| `judge_accuracy` | 0.8125 | 0.3750 | 0.8125 | -0.4375 | Restored |
| Data Quality Status | PASSED | FAILED | PASSED | — | Restored |

## 2. Sample Side-by-Side Question Evidence

### Sample Question 1: `q001`
**Question**: What is 'SafeRAG: A Large-Language-Model-Based Multistage Retrieval-Augmented Framework for Oil and Gas Safety Report Generation' about?

**Ground Truth**: `Summary In high-risk industrial settings, leveraging large language models (LLMs) for automated accident analysis and generating safety reports has emerged as an efficient workflow. However, this approach is fundamentally constrained by the models’ inherent knowledge limitations, frequently resulting in analyses that lack domain-specific understanding and regulatory alignment. To tackle this issue, we introduce SafeRAG, a multistage retrieval-augmented framework for safety report generation. Specifically, the framework uses an entity-centric approach that prompts the LLMs to internally generate domain-specific knowledge. Concurrently, it performs a hierarchical retrieval of external regulations relevant to the accident at topic, concept, and context levels. To obtain well-structured reports, we leverage prompt engineering, integrating internal and external knowledge. Furthermore, a domain-expert persona is also assigned to help LLMs analyze accidents from a specific perspective. To evaluate our approach, we construct a data set from 10,818 accident-description/report pairs collected from real-world industry reports. Experiments show that SafeRAG substantially outperforms baseline LLMs on metrics that include bidirectional encoder representations from transformers (BERTScore) and bidirectional auto-regressive transformers (BARTScore), demonstrating the effectiveness of our approach.`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.2118/234689-pa', '10.55041/isjem07213', '10.20944/preprints202604.0339.v1', '10.21203/rs.3.rs-9770645/v1']` | Hit | 0.3117 | Summary In high-risk industrial settings, leveraging large language models (LLMs) for automated accident analysis and generating safety reports has emerged as an efficient workflow. |
| **Corrupted** | `['10.55041/isjem07213', '10.20944/preprints202604.0339.v1', '10.21203/rs.3.rs-9770645/v1', '10.21203/rs.3.rs-9882260/v1']` | Miss | 0.0795 | Abstract - This work focuses on the two crucial bottlenecks in Retrieval-Augmented Generation (RAG): high inference latency and expensive computation cost. |
| **Repaired** | `['10.2118/234689-pa', '10.55041/isjem07213', '10.20944/preprints202604.0339.v1', '10.21203/rs.3.rs-9770645/v1']` | Hit | 0.3117 | Summary In high-risk industrial settings, leveraging large language models (LLMs) for automated accident analysis and generating safety reports has emerged as an efficient workflow. |

### Sample Question 2: `q002`
**Question**: Who authored 'SafeRAG: A Large-Language-Model-Based Multistage Retrieval-Augmented Framework for Oil and Gas Safety Report Generation'?

**Ground Truth**: `Qianwen Cao, Chiyu Zhang, Junxiong Ning, Gongru Li`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.2118/234689-pa', '10.20944/preprints202604.0339.v1', '10.21203/rs.3.rs-9770645/v1', '10.55041/isjem07213']` | Hit | 1.0000 | Qianwen Cao, Chiyu Zhang, Junxiong Ning, Gongru Li |
| **Corrupted** | `['10.20944/preprints202604.0339.v1', '10.21203/rs.3.rs-9770645/v1', '10.55041/isjem07213', '10.63646/kpqm1958']` | Miss | 0.0000 | Ruotong Wang, Nyutian Long, Shunqi Liu, Yuxi Wang, Zhen Qi, Huajun Zhang |
| **Repaired** | `['10.2118/234689-pa', '10.20944/preprints202604.0339.v1', '10.21203/rs.3.rs-9770645/v1', '10.55041/isjem07213']` | Hit | 1.0000 | Qianwen Cao, Chiyu Zhang, Junxiong Ning, Gongru Li |

### Sample Question 3: `q003`
**Question**: When was 'SafeRAG: A Large-Language-Model-Based Multistage Retrieval-Augmented Framework for Oil and Gas Safety Report Generation' published on?

**Ground Truth**: `2026-08-01`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.2118/234689-pa', '10.21203/rs.3.rs-9770645/v1', '10.20944/preprints202604.0339.v1', '10.55041/isjem07213']` | Hit | 1.0000 | 2026-08-01 |
| **Corrupted** | `['10.21203/rs.3.rs-9770645/v1', '10.20944/preprints202604.0339.v1', '10.55041/isjem07213', '10.63646/kpqm1958']` | Miss | 0.0000 | 2026-05-22 |
| **Repaired** | `['10.2118/234689-pa', '10.21203/rs.3.rs-9770645/v1', '10.20944/preprints202604.0339.v1', '10.55041/isjem07213']` | Hit | 1.0000 | 2026-08-01 |

### Sample Question 4: `q004`
**Question**: What categories does 'SafeRAG: A Large-Language-Model-Based Multistage Retrieval-Augmented Framework for Oil and Gas Safety Report Generation' belong to?

**Ground Truth**: `journal-article`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.2118/234689-pa', '10.21203/rs.3.rs-9770645/v1', '10.55041/isjem07213', '10.20944/preprints202604.0339.v1']` | Hit | 1.0000 | journal-article |
| **Corrupted** | `['10.21203/rs.3.rs-9770645/v1', '10.55041/isjem07213', '10.20944/preprints202604.0339.v1', '10.21203/rs.3.rs-9882260/v1']` | Miss | 0.0000 | posted-content |
| **Repaired** | `['10.2118/234689-pa', '10.21203/rs.3.rs-9770645/v1', '10.55041/isjem07213', '10.20944/preprints202604.0339.v1']` | Hit | 1.0000 | journal-article |

### Sample Question 5: `q005`
**Question**: What is 'Microsoft Azure artificial intelligence / machine learning hackathon for development of retrieval-augmented generation large language model' about?

**Ground Truth**: `The US Army Corps of Engineers (USACE) Civil Works (CW) research and development (R&D) mission is to address challenging environmental sustainability problems through innovative science and engineering, which helps to ensure a safer, more prosperous, and more resilient nation. To achieve this, the US Army Engineer Research and Development Center (ERDC) plans, executes, leads, and directs many R&D programs in coordination with USACE Headquarters, Districts, and Divisions through its multiple strategic focus areas, which include infrastructure, water modeling, crisis preparedness, ecosystem, sediment management, data, artificial intelligence, and robotics. In this process, much information is generated, including internal progress reviews, financial reports, scopes of work, work package planning, and success stories.`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.21079/11681/50309', '10.63646/kpqm1958', '10.35314/3y9hy151', '10.70121/001c.158711']` | Hit | 0.5600 | The US Army Corps of Engineers (USACE) Civil Works (CW) research and development (R&D) mission is to address challenging environmental sustainability problems through innovative science and engineering, which helps to ensure a safer, more prosperous, and more resilient nation. |
| **Corrupted** | `['10.63646/kpqm1958', '10.35314/3y9hy151', '10.70121/001c.158711', '10.32473/flairs.39.1.141782']` | Miss | 0.0678 | The rapid evolution of large language models (LLMs) has catalyzed a shift from passive AI systems toward autonomous agentic architectures capable of reasoning, memory, tool use, and multi-agent collaboration. |
| **Repaired** | `['10.21079/11681/50309', '10.63646/kpqm1958', '10.35314/3y9hy151', '10.70121/001c.158711']` | Hit | 0.5600 | The US Army Corps of Engineers (USACE) Civil Works (CW) research and development (R&D) mission is to address challenging environmental sustainability problems through innovative science and engineering, which helps to ensure a safer, more prosperous, and more resilient nation. |

### Sample Question 6: `q006`
**Question**: Who authored 'Microsoft Azure artificial intelligence / machine learning hackathon for development of retrieval-augmented generation large language model'?

**Ground Truth**: `Janet L. Autrey, Lacey S. Duckworth, Ashly N. Horner, Thomas Sigler, Victoria D. Moore`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.21079/11681/50309', '10.63646/kpqm1958', '10.70121/001c.158711', '10.22214/ijraset.2026.82233']` | Hit | 1.0000 | Janet L. Autrey, Lacey S. Duckworth, Ashly N. Horner, Thomas Sigler, Victoria D. Moore |
| **Corrupted** | `['10.63646/kpqm1958', '10.35314/3y9hy151', '10.70121/001c.158711', '10.22214/ijraset.2026.82233']` | Miss | 0.0870 | Ben J. Weber, Clara M. Hofmann, Amara N. Okoye |
| **Repaired** | `['10.21079/11681/50309', '10.63646/kpqm1958', '10.70121/001c.158711', '10.22214/ijraset.2026.82233']` | Hit | 1.0000 | Janet L. Autrey, Lacey S. Duckworth, Ashly N. Horner, Thomas Sigler, Victoria D. Moore |

### Sample Question 7: `q007`
**Question**: When was 'Microsoft Azure artificial intelligence / machine learning hackathon for development of retrieval-augmented generation large language model' published on?

**Ground Truth**: `2026-07-01`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.21079/11681/50309', '10.63646/kpqm1958', '10.70121/001c.158711', '10.35314/3y9hy151']` | Hit | 1.0000 | 2026-07-01 |
| **Corrupted** | `['10.63646/kpqm1958', '10.35314/3y9hy151', '10.70121/001c.158711', '10.52060/juptik.v4i1.4318']` | Miss | 0.0000 | 2026-06-30 |
| **Repaired** | `['10.21079/11681/50309', '10.63646/kpqm1958', '10.70121/001c.158711', '10.35314/3y9hy151']` | Hit | 1.0000 | 2026-07-01 |

### Sample Question 8: `q008`
**Question**: What categories does 'Microsoft Azure artificial intelligence / machine learning hackathon for development of retrieval-augmented generation large language model' belong to?

**Ground Truth**: `report`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.21079/11681/50309', '10.63646/kpqm1958', '10.35314/3y9hy151', '10.1111/exsy.70341']` | Hit | 1.0000 | report |
| **Corrupted** | `['10.63646/kpqm1958', '10.35314/3y9hy151', '10.70121/001c.158711', '10.21203/rs.3.rs-9770645/v1']` | Miss | 0.0000 | journal-article |
| **Repaired** | `['10.21079/11681/50309', '10.63646/kpqm1958', '10.35314/3y9hy151', '10.1111/exsy.70341']` | Hit | 1.0000 | report |

### Sample Question 9: `q009`
**Question**: What is 'Hallucination in Large Language Models and Retrieval-Augmented Generation: Mechanisms, Mitigation, and Evaluation' about?

**Ground Truth**: `Large language models have demonstrated strong generative capability in question answering, dialogue, and other knowledge-intensive tasks. However, their outputs remain vulnerable to hallucination, including factual errors, unsupported claims, spurious citations, and distorted reasoning. Retrieval-augmented generation (RAG) has been proposed as a practical remedy because it supplements parametric knowledge with external evidence retrieved at inference time. Yet RAG does not guarantee truthfulness or attribution by default. Errors may arise during query formulation, document retrieval, evidence aggregation, and answer grounding. This paper reviews the relationship between hallucination and RAG from three perspectives: mechanism, mitigation, and evaluation. First, the major causes of hallucination in both vanilla LLMs and RAG-enhanced systems are analyzed. Second, the principal mitigation strategies are organized into retrieval optimization, evidence-grounded generation, and post-generation verification. Third, the main evaluation dimensions are examined, including factuality, faithfulness, attribution quality, and retrieval relevance. It is argued that RAG should not be treated as a complete solution to hallucination. Its value lies in enabling externally grounded generation, but its effectiveness depends on the reliability of retrieval, the fidelity of evidence use, and the rigor of evaluation. Future work should prioritize attribution-aware generation, conflict-sensitive reasoning, and unified evaluation protocols for trustworthy LLM systems.`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.54254/2753-8818/2026.dl34055', '10.63646/kpqm1958', '10.70121/001c.158711', '10.1093/sleep/zsag091.0346']` | Hit | 0.1871 | Large language models have demonstrated strong generative capability in question answering, dialogue, and other knowledge-intensive tasks. |
| **Corrupted** | `['10.54254/2753-8818/2026.dl34055', '10.63646/kpqm1958', '10.70121/001c.158711', '10.35314/3y9hy151']` | Hit | 0.1871 | Large language models have demonstrated strong generative capability in question answering, dialogue, and other knowledge-intensive tasks. |
| **Repaired** | `['10.54254/2753-8818/2026.dl34055', '10.63646/kpqm1958', '10.70121/001c.158711', '10.1093/sleep/zsag091.0346']` | Hit | 0.1871 | Large language models have demonstrated strong generative capability in question answering, dialogue, and other knowledge-intensive tasks. |

### Sample Question 10: `q010`
**Question**: Who authored 'Hallucination in Large Language Models and Retrieval-Augmented Generation: Mechanisms, Mitigation, and Evaluation'?

**Ground Truth**: `Haopeng Yang`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.54254/2753-8818/2026.dl34055', '10.63646/kpqm1958', '10.1093/sleep/zsag091.0346', '10.70121/001c.158711']` | Hit | 1.0000 | Haopeng Yang |
| **Corrupted** | `['10.54254/2753-8818/2026.dl34055', '10.63646/kpqm1958', '10.1093/sleep/zsag091.0346', '10.70121/001c.158711']` | Hit | 1.0000 | Haopeng Yang |
| **Repaired** | `['10.54254/2753-8818/2026.dl34055', '10.63646/kpqm1958', '10.1093/sleep/zsag091.0346', '10.70121/001c.158711']` | Hit | 1.0000 | Haopeng Yang |

### Sample Question 11: `q011`
**Question**: When was 'Hallucination in Large Language Models and Retrieval-Augmented Generation: Mechanisms, Mitigation, and Evaluation' published on?

**Ground Truth**: `2026-06-01`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.54254/2753-8818/2026.dl34055', '10.63646/kpqm1958', '10.70121/001c.158711', '10.1093/sleep/zsag091.0346']` | Hit | 1.0000 | 2026-06-01 |
| **Corrupted** | `['10.54254/2753-8818/2026.dl34055', '10.63646/kpqm1958', '10.70121/001c.158711', '10.1093/sleep/zsag091.0346']` | Hit | 1.0000 | 2026-06-01 |
| **Repaired** | `['10.54254/2753-8818/2026.dl34055', '10.63646/kpqm1958', '10.70121/001c.158711', '10.1093/sleep/zsag091.0346']` | Hit | 1.0000 | 2026-06-01 |

### Sample Question 12: `q012`
**Question**: What categories does 'Hallucination in Large Language Models and Retrieval-Augmented Generation: Mechanisms, Mitigation, and Evaluation' belong to?

**Ground Truth**: `journal-article`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.54254/2753-8818/2026.dl34055', '10.70121/001c.158711', '10.63646/kpqm1958', '10.1093/sleep/zsag091.0346']` | Hit | 1.0000 | journal-article |
| **Corrupted** | `['10.54254/2753-8818/2026.dl34055', '10.70121/001c.158711', '10.63646/kpqm1958', '10.1093/sleep/zsag091.0346']` | Hit | 1.0000 | journal-article |
| **Repaired** | `['10.54254/2753-8818/2026.dl34055', '10.70121/001c.158711', '10.63646/kpqm1958', '10.1093/sleep/zsag091.0346']` | Hit | 1.0000 | journal-article |

### Sample Question 13: `q013`
**Question**: What is 'Retrieval-Augmented Large Language Model Agents for Automated Scientific Literature Review Generation' about?

**Ground Truth**: `This study investigates a method that integrates retrieval-augmented mechanisms into large language model agents for scientific literature review generation. The approach addresses the limitations of traditional review models that rely on parametric knowledge with insufficient timeliness and limited coverage. Incorporating external document retrieval and dynamic information fusion into the generation process enhances the accuracy and completeness of the output. The overall framework consists of query encoding, semantic retrieval, document filtering, knowledge fusion, language modeling, task planning, memory storage, and reinforcement optimization, forming a closed loop of retrieval, understanding, and generation. Relevant document fragments are first retrieved through semantic vector search to ensure comprehensive and reliable information sources. These external representations are then integrated with the internal embeddings of the language model through weighted fusion, which preserves fluency while maintaining factual grounding. The task planning module constrains logical flow and text structure, and reinforcement learning optimization further improves relevance and consistency. Comparative experiments on large-scale scientific literature datasets demonstrate that the method outperforms existing approaches on ROUGE, BLEU, METEOR, and diversity metrics, validating its effectiveness and practicality. The findings show that combining retrieval augmentation with agent architectures can significantly improve coverage, accuracy, and language quality in review generation, providing a feasible solution for knowledge organization in complex literature environments.`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.20944/preprints202604.0339.v1', '10.63646/kpqm1958', '10.55041/isjem07213', '10.54254/2753-8818/2026.dl34055']` | Hit | 0.2303 | This study investigates a method that integrates retrieval-augmented mechanisms into large language model agents for scientific literature review generation. |
| **Corrupted** | `['10.20944/preprints202604.0339.v1', '10.63646/kpqm1958', '10.55041/isjem07213', '10.54254/2753-8818/2026.dl34055']` | Hit | 0.2303 | This study investigates a method that integrates retrieval-augmented mechanisms into large language model agents for scientific literature review generation. |
| **Repaired** | `['10.20944/preprints202604.0339.v1', '10.63646/kpqm1958', '10.55041/isjem07213', '10.54254/2753-8818/2026.dl34055']` | Hit | 0.2303 | This study investigates a method that integrates retrieval-augmented mechanisms into large language model agents for scientific literature review generation. |

### Sample Question 14: `q014`
**Question**: Who authored 'Retrieval-Augmented Large Language Model Agents for Automated Scientific Literature Review Generation'?

**Ground Truth**: `Ruotong Wang, Nyutian Long, Shunqi Liu, Yuxi Wang, Zhen Qi, Huajun Zhang`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.20944/preprints202604.0339.v1', '10.63646/kpqm1958', '10.55041/isjem07213', '10.70121/001c.158711']` | Hit | 1.0000 | Ruotong Wang, Nyutian Long, Shunqi Liu, Yuxi Wang, Zhen Qi, Huajun Zhang |
| **Corrupted** | `['10.20944/preprints202604.0339.v1', '10.63646/kpqm1958', '10.55041/isjem07213', '10.70121/001c.158711']` | Hit | 1.0000 | Ruotong Wang, Nyutian Long, Shunqi Liu, Yuxi Wang, Zhen Qi, Huajun Zhang |
| **Repaired** | `['10.20944/preprints202604.0339.v1', '10.63646/kpqm1958', '10.55041/isjem07213', '10.70121/001c.158711']` | Hit | 1.0000 | Ruotong Wang, Nyutian Long, Shunqi Liu, Yuxi Wang, Zhen Qi, Huajun Zhang |

### Sample Question 15: `q015`
**Question**: When was 'Retrieval-Augmented Large Language Model Agents for Automated Scientific Literature Review Generation' published on?

**Ground Truth**: `2026-04-06`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.20944/preprints202604.0339.v1', '10.63646/kpqm1958', '10.70121/001c.158711', '10.55041/isjem07213']` | Hit | 1.0000 | 2026-04-06 |
| **Corrupted** | `['10.20944/preprints202604.0339.v1', '10.63646/kpqm1958', '10.70121/001c.158711', '10.55041/isjem07213']` | Hit | 1.0000 | 2026-04-06 |
| **Repaired** | `['10.20944/preprints202604.0339.v1', '10.63646/kpqm1958', '10.70121/001c.158711', '10.55041/isjem07213']` | Hit | 1.0000 | 2026-04-06 |

### Sample Question 16: `q016`
**Question**: What categories does 'Retrieval-Augmented Large Language Model Agents for Automated Scientific Literature Review Generation' belong to?

**Ground Truth**: `posted-content`

| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |
| --- | --- | --- | ---: | --- |
| **Baseline** | `['10.20944/preprints202604.0339.v1', '10.63646/kpqm1958', '10.55041/isjem07213', '10.70121/001c.158711']` | Hit | 1.0000 | posted-content |
| **Corrupted** | `['10.20944/preprints202604.0339.v1', '10.63646/kpqm1958', '10.55041/isjem07213', '10.70121/001c.158711']` | Hit | 1.0000 | posted-content |
| **Repaired** | `['10.20944/preprints202604.0339.v1', '10.63646/kpqm1958', '10.55041/isjem07213', '10.70121/001c.158711']` | Hit | 1.0000 | posted-content |

