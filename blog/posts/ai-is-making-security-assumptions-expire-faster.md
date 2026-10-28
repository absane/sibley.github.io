---
title: "AI Is Making Security Assumptions Expire Faster"
date: "2026-10-28"
summary: "AI can reduce the effort needed to explore an attack path while adding new questions about trust and authority. Security teams need evidence that their controls can keep pace."
tags:
  - Commentary
  - Artificial Intelligence
  - Offensive Security
draft: false
---

An overlooked application can remain exposed for years. A questionable access rule can survive several audits. A business process can depend on everyone recognizing when a request feels wrong.

Sometimes those weaknesses persist because exploiting them takes time, context, and persistence. Someone has to connect the pieces. Security teams should be careful about treating that effort as a dependable layer of protection.

My concern about AI in cybersecurity starts there: it can make more of that effort affordable. A weakness that once demanded sustained attention may become practical to revisit repeatedly. A process that depended on an attacker losing patience deserves another look.

That changes how long we should be comfortable leaving our assumptions untested.

## The economics of persistence

A large part of security work involves reading, sorting, comparing, and deciding what to investigate next. Documentation, source code, application behavior, error messages, and old research all contain clues. Working through them consumes attention, even when the eventual discovery is straightforward.

AI assistance can reduce some of that overhead. The important question is how much useful work survives verification. A plausible explanation of a vulnerability still needs evidence. Generated code still needs review. A confident answer can send an investigation in the wrong direction.

Even with those limitations, partial improvements matter. If the cost of exploring a possibility falls, more possibilities become worth exploring. An attacker does not need every attempt to work for that to change the economics of an operation.

The [NCSC's May 2025 assessment of AI's impact through 2027](https://www.ncsc.gov.uk/report/impact-ai-cyber-threat-now-2027) anticipated more effective intrusion activity and greater pressure on unpatched systems. It also assessed fully automated, end-to-end advanced attacks as unlikely within that horizon. Those were forecasts, not proof of what every attacker can do today.

My reading is that organizations should plan for faster, more persistent investigation of familiar weaknesses while continuing to question sweeping claims about autonomous capability.

## Familiar trust problems gain new leverage

In my [2023 article on AI and social engineering](https://versprite.com/resources/blog/the-intersection-of-artificial-intelligence-and-social-engineering-next-generation-threats/), I explored how generated language, voice, and video could strengthen impersonation and deception. The underlying problem remains recognizable: an organization grants access or authority because a request appears credible.

That is a fragile foundation when credibility can be manufactured.

A payment approval process should remain defensible when a message sounds like the person who normally sends it. A help desk should have a reliable way to verify identity when a caller knows the right terminology. Training helps, but the process needs to withstand convincing requests as well as obviously suspicious ones.

AI applications introduce another version of this problem. We increasingly ask software to read outside material and then act on what it finds. The application has to preserve a boundary between information it encounters and instructions it is authorized to follow.

[OWASP's guidance on prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) describes how external content can influence model behavior, including in systems connected to tools and sensitive information. Its recommendations include least privilege, controls around privileged actions, and adversarial testing.

Consider a hypothetical internal assistant that reads a supplier document and can create support tickets. Its risk changes considerably if it can also retrieve unrelated customer records or change account permissions. The same misleading document could have very different consequences depending on the authority surrounding the model.

An assessment should follow those permissions all the way through. What can the application read? What can it change? Which component makes the final authorization decision? What happens when the outside material is deliberately misleading?

## Defenders have to preserve the business

AI can help defenders investigate alerts, review changes, and organize evidence. There is plenty of useful work to do before giving a system permission to alter production infrastructure.

The distinction matters because defensive action carries operational consequences. Disabling an account, isolating a host, or changing a firewall rule might interrupt the very service the security team is protecting. Faster decisions only help when the organization can tolerate and recover from mistakes.

Dave Chismon's [September 2026 NCSC commentary on agentic defense](https://www.ncsc.gov.uk/blogs/one-does-not-simply-defend-agentically) makes this constraint explicit. It proposes evaluating actions against factors including their scope, criticality, and recoverability. That is a useful starting point for deciding where automation belongs.

I would look for bounded tasks with observable outcomes first. Summarizing evidence for an analyst and changing a production system deserve different evaluation criteria. Each needs a clear owner, a way to inspect what happened, and a response when the result is wrong.

Human approval also needs substance. A person clicking through a polished recommendation without enough context provides little assurance. Approval should expose the proposed action, supporting evidence, affected systems, and likely consequences in a form the reviewer can actually assess.

## What I would ask a security team to demonstrate

The useful output of this discussion is a set of things an organization can test:

1. **An exposed service gets an owner and a decision.** Show how the team identifies who is responsible and moves from discovery to remediation, restriction, or an explicit risk decision.
2. **A convincing impersonation meets independent verification.** Test whether a sensitive workflow can establish authority without relying on the apparent familiarity of a message or voice.
3. **An AI assistant stays within its assigned access.** Check the application with misleading documents, conflicting instructions, and requests involving another user's information. Verify enforcement at the service and data layers.
4. **An automated action leaves usable evidence.** Establish what was proposed, which inputs supported it, what was approved, and what actually changed. Keep enough context to investigate failure.
5. **A mistaken action can be contained and reversed.** Exercise recovery within the scope where automation is allowed, including the people and systems needed to restore service.

These demonstrations should produce evidence that someone else can inspect and repeat. A convincing model response, a successful demo, or a long list of findings offers limited assurance on its own.

AI creates real opportunities for security teams. It also puts pressure on organizations whose defenses depend on slow investigation, convincing appearances, or loosely controlled authority. The practical response is to identify those dependencies and test them while there is still time to change them.

The standard I would hold onto is simple: faster work should lead to better-supported decisions. As AI takes on more of the work, the evidence and accountability need to keep up.
