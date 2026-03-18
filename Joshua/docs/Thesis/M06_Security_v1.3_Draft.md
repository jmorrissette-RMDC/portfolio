# Paper M06: Security MADs - Defense in Depth

**Version**: 1.3 Draft **Date**: October 17, 2025 **Status**: Draft - Awaiting Review

***

## Abstract

This paper examines the Security domain within the Joshua ecosystem, focusing on four specialized MADs that implement comprehensive defense-in-depth security. The authentication and authorization MAD manages identity verification and access control. The cryptographic services MAD handles all encryption, signatures, and cryptographic operations. The security operations MAD monitors for threats, coordinates testing, and investigates anomalies. The secrets management MAD securely stores and controls access to sensitive credentials. Together, these MADs protect the ecosystem across all security layers: identity, data protection, threat detection, and credential management. This demonstrates how the MAD pattern can implement sophisticated security through specialized components that make robust protection simple and automatic rather than requiring constant security expertise from users and other MADs.

**Keywords**: authentication, cryptography, security operations, secrets management, defense in depth, identity management

***

## 1. Introduction

### 1.1 Security as Layered Defense

Effective security requires protection across multiple layers. **Identity verification** ensures only authorized entities access system resources. **Cryptographic protection** secures data at rest and in transit. **Threat monitoring** detects and responds to security anomalies. **Credential management** protects the keys that unlock system capabilities.

Systems that address these layers inconsistently create security weaknesses. Strong authentication is undermined by weak encryption. Robust cryptography is compromised by exposed credentials. Effective monitoring is useless if threats exploit weak identity controls. Comprehensive security demands coordinated protection across all layers.

Traditional security implementations distribute responsibility across development teams. Developers implement authentication. Operations teams manage monitoring. Infrastructure teams handle cryptography. Security teams oversee credentials. This distribution creates gaps where responsibility boundaries blur and comprehensive protection suffers.

### 1.2 Unified Security Architecture

The Security domain in Joshua implements defense-in-depth through four specialized MADs, each focusing on a specific security layer while coordinating to provide comprehensive protection.

The **authentication and authorization MAD** manages identity—verifying who users and systems are, and what they're allowed to do. Multi-factor authentication, role-based access control, session management, and context-aware security all centralize in this component.

The **cryptographic services MAD** handles all cryptographic operations—encryption, decryption, signing, verification, key management, and certificate handling. Other MADs request cryptographic services without needing cryptographic expertise.

The **security operations MAD** monitors ecosystem security—detecting anomalies, coordinating penetration tests, investigating suspicious activity, and managing security reviews. Continuous monitoring and proactive testing ensure security posture remains strong.

The **secrets management MAD** handles all sensitive credentials—API keys, passwords, tokens, certificates. Secure generation, storage, rotation, and access control happen automatically without requiring manual secret management.

### 1.3 Security Made Invisible

A key Security domain principle: robust security should be invisible to users and other MADs. Security should be automatic, not requiring constant security expertise or attention.

Users interact through the human interface MAD without manually managing authentication. Sessions are secured automatically. Multi-factor authentication happens naturally when risk levels warrant it. Authorization checks occur transparently.

Other MADs request cryptographic protection conversationally without understanding cipher modes or key lengths. They request secrets without managing storage or rotation. They benefit from security monitoring without implementing detection themselves.

This invisible security makes robust protection achievable. When security requires constant expertise and attention, it becomes a burden that's often neglected or implemented incorrectly. When security is automatic and invisible, robust protection becomes the default state.

### 1.4 Empirical Validation

The Security MAD architecture described in this paper has been empirically validated through two case studies:

**V0 Architecture (Paper C01 / Appendix A):** The Cellular Monolith generation operated within containerized environments with secrets management for API keys, encrypted conversation storage protecting intellectual property, and access control ensuring only authorized LLMs could participate in document generation. The cryptographic MAD secured the delta format optimization discovery, protecting the 19× throughput improvement insight. **See Appendix A for complete case study details.**

**V1 Architecture (Paper C02 / Appendix B):** The Synergos autonomous creation validated the security audit MAD through code review of generated deliverables, the secrets management MAD through secure handling of development credentials, and the authentication MAD through access control to the five-phase workflow. The consensus validation process operated under encrypted channels protecting analyst assessments. **See Appendix B for complete case study details.**

Together, these case studies provide empirical evidence that the Security domain operates as designed, successfully providing invisible layered defense while enabling complex multi-LLM operations.

***

## 2. Authentication and Authorization: Identity Management

### 2.1 The Identity Challenge

System security begins with identity. Before determining what a user can do, systems must verify who the user is. Before granting access to resources, systems must confirm authorization. Without robust identity management, all other security measures fail—encryption protects data from wrong parties only if identity verification prevents wrong parties from authenticating as authorized users.

Traditional authentication varies widely in robustness. Simple password authentication is vulnerable to credential theft. Multi-factor authentication adds security but increases complexity. Context-aware authentication adapts security to risk levels but requires sophisticated implementation. Session management must balance security with user convenience.

### 2.2 Multi-Factor Authentication

The authentication and authorization MAD implements flexible multi-factor authentication adapting to risk levels. Low-risk operations might require only password authentication. Moderate-risk operations add time-based codes or push notifications. High-risk operations demand additional factors—biometric verification, hardware tokens, or confirmation from trusted devices.

This risk-based approach balances security with usability. Users aren't burdened with excessive authentication for routine operations. Critical operations receive protection proportional to their sensitivity. The MAD determines appropriate authentication levels based on operation risk, user context, and security policy.

Authentication factors vary by capability. Password verification validates knowledge. Time-based codes from authenticator apps validate possession of registered devices. Biometric verification validates physical presence. Hardware security keys validate cryptographically protected devices. The MAD coordinates these factors, presenting unified authentication flows while managing multiple verification methods.

### 2.3 Role-Based Access Control

Authentication establishes identity—authorization determines permitted actions. The MAD implements role-based access control where permissions attach to roles rather than individual users.

Roles reflect organizational functions. Developer roles receive permissions for code modification and deployment operations. Analyst roles receive data access but not modification. Administrator roles receive system configuration privileges. Users are assigned appropriate roles based on their responsibilities.

This role-based approach simplifies permission management. Granting new capabilities means assigning roles, not individually managing thousands of permission flags. Role changes propagate automatically—when user responsibilities change, role reassignment updates all associated permissions. New users receive appropriate permissions by role assignment without requiring detailed permission configuration.

Fine-grained permissions complement roles for exceptional cases. While most access follows role definitions, specific users might require additional permissions or restrictions beyond their role's baseline. The MAD supports these exceptions while maintaining role-based structure as the primary permission mechanism.

### 2.4 Session Management

After authentication, sessions maintain authenticated state without requiring continuous re-authentication. The MAD implements secure session management using JSON Web Tokens that balance security with usability.

Session tokens contain encrypted authentication state, enabling stateless session verification. The MAD validates tokens cryptographically without requiring centralized session storage for every verification. This approach scales effectively—no session database bottleneck limits concurrent authenticated users.

Session lifetime adapts to security context. Interactive user sessions might last hours with automatic renewal on activity. API sessions might last shorter periods. High-security contexts might require session re-authentication even during active use. The MAD manages these varying lifetime patterns based on security policy and risk assessment.

Session invalidation handles security events immediately. When user credentials change, when user roles are modified, or when security incidents require access termination, session invalidation forces re-authentication. The MAD coordinates invalidation across all session instances, preventing continued access after security state changes.

### 2.5 Context-Aware Security

Security decisions benefit from contextual awareness. Access patterns, geographic locations, device types, and behavioral patterns inform risk assessment. The MAD implements context-aware security that adapts authentication requirements and authorization decisions to observed context.

Unusual access patterns trigger enhanced verification. A user accessing from a new location, a device accessing outside normal hours, or behavioral patterns deviating from established norms all indicate elevated risk. The MAD can require additional authentication factors, limit operation scope, or flag activity for security operations review.

This context awareness provides security without excessive friction. Users operating in normal patterns experience minimal authentication burden. Anomalous patterns receive appropriate scrutiny. The balance between security and usability adapts to actual risk rather than applying uniform requirements regardless of context.

***

## 3. Cryptographic Services: Data Protection

### 3.1 The Cryptography Challenge

Data protection depends on cryptographic operations—encryption secures data at rest and in transit, digital signatures verify authenticity and integrity, key management ensures cryptographic keys remain protected. But cryptography is complex—cipher selection, key lengths, initialization vectors, padding schemes, and authentication modes all require expertise to implement correctly.

Cryptographic vulnerabilities arise from implementation errors more often than mathematical weaknesses. Developers use weak key lengths, apply incorrect cipher modes, fail to authenticate encrypted data, or mismanage initialization vectors. These implementation errors create security vulnerabilities even when cryptographic algorithms themselves are sound.

### 3.2 Encryption Services

The cryptographic services MAD provides encryption as a simple conversational service. Other MADs request "encrypt this data" without specifying cipher modes, key lengths, or authentication schemes. The cryptographic services MAD applies appropriate encryption based on data sensitivity and usage patterns.

Encryption at rest protects stored data. Database contents, file system storage, and configuration data all receive encryption automatically. The MAD selects appropriate encryption schemes—symmetric encryption for bulk data, authenticated encryption preventing tampering, and key rotation ensuring long-term protection even if keys are eventually compromised.

Encryption in transit protects communication. All conversation bus messages are encrypted end-to-end. External API traffic uses TLS with strong cipher suites. The MAD manages certificate provisioning, renewal, and validation without requiring other MADs to understand certificate chains and validation rules.

Key management happens automatically. The MAD generates cryptographic keys with appropriate entropy, stores them securely, rotates them according to policy, and revokes them when necessary. Other MADs request encryption without managing keys directly—the cryptographic services MAD handles key lifecycle invisibly.

### 3.3 Digital Signatures

Digital signatures verify authenticity and integrity. When messages must be verifiably attributed to their sender, when data integrity must be cryptographically assured, digital signatures provide mathematical proof.

The MAD provides signing services conversationally. A MAD requests "sign this message" and receives the signature without implementing signing algorithms. Verification works similarly—"verify this signature" confirms authenticity without requiring the verifying MAD to understand signature schemes.

This signature abstraction enables robust non-repudiation. Messages can be proven to originate from specific MADs. Documents can be verified as unmodified since signing. Authentication tokens can be validated cryptographically. All without requiring widespread cryptographic expertise across all MADs.

### 3.4 Certificate Management

Public key infrastructure requires certificate management—generating certificate signing requests, obtaining certificates from certificate authorities, managing certificate chains, monitoring expiration, and renewing before expiry. The cryptographic services MAD handles this complexity automatically.

TLS certificates for external communication are provisioned automatically. The MAD generates key pairs, creates signing requests, obtains certificates from authorities, configures servers with certificates, monitors expiration, and renews well before certificates expire. External communication remains secure without requiring manual certificate management.

Internal certificates for MAD-to-MAD authentication follow similar patterns. The MAD operates as internal certificate authority, issuing certificates to MADs, managing trust chains, handling revocation when needed, and ensuring all MADs trust appropriate certificate authorities.

### 3.5 Cryptographic Best Practices

The MAD ensures cryptographic best practices apply uniformly. Appropriate key lengths, secure cipher modes, authenticated encryption, and proper initialization vector handling all happen automatically. Other MADs benefit from state-of-the-art cryptography without implementing it themselves.

As cryptographic best practices evolve—new algorithms become preferred, key length recommendations increase, cipher modes are discovered vulnerable—the cryptographic services MAD updates its implementations. These improvements propagate automatically to all MADs. No individual MAD needs updating when cryptographic best practices evolve.

***

## 4. Security Operations: Threat Detection and Response

### 4.1 The Monitoring Challenge

Security threats manifest in various forms—unauthorized access attempts, anomalous behavior patterns, exploitation attempts, configuration vulnerabilities, and insider threats. Detecting these threats requires continuous monitoring, pattern analysis, anomaly detection, and threat intelligence. Responding effectively requires investigation capabilities, incident coordination, and remediation workflows.

Traditional security operations rely on security operations centers where analysts monitor dashboards, investigate alerts, and coordinate responses. This centralized approach creates bottlenecks—limited analyst capacity, alert fatigue from false positives, and delayed responses when threats emerge.

### 4.2 Continuous Security Monitoring

The security operations MAD implements continuous monitoring across ecosystem activity. All conversation bus messages are analyzed for anomalous patterns. Authentication attempts are monitored for credential stuffing or brute force attacks. Resource access patterns are evaluated for unauthorized data access. System configurations are checked against security baselines.

This comprehensive monitoring operates automatically without requiring constant human attention. The MAD analyzes activity continuously, identifies concerning patterns, investigates potential threats, and alerts when human intervention is warranted. Security monitoring becomes automated rather than requiring dedicated analyst attention.

Anomaly detection adapts to normal patterns. The MAD learns typical access patterns, usual authentication timing, normal resource utilization, and expected communication flows. Deviations from these learned patterns trigger investigation—not immediate alarms, but automated analysis determining whether deviations represent genuine threats or benign variations.

### 4.3 Penetration Testing

Proactive security testing identifies vulnerabilities before adversaries exploit them. The security operations MAD coordinates penetration testing—authorized attempts to compromise system security, simulating attacker behavior to discover weaknesses.

Penetration testing happens through specialized ephemeral teams. The security operations MAD composes security testing eMADs with expertise in specific attack vectors—web application security, network penetration, social engineering, or credential compromise. These eMADs attempt to breach defenses using known attack patterns and techniques.

Testing results inform security improvements. Discovered vulnerabilities trigger remediation—the security operations MAD creates conversations with affected components, requesting security patches. The meta-programming component implements fixes. Testing cycles repeat to verify remediation effectiveness.

This continuous testing approach ensures security remains robust as the ecosystem evolves. New capabilities are tested before production deployment. Configuration changes trigger security validation. Periodic comprehensive testing provides ongoing security assurance.

### 4.4 Incident Investigation

When security anomalies warrant investigation, the security operations MAD conducts thorough analysis. It examines conversation history for suspicious patterns, reviews authentication logs for credential compromise evidence, analyzes resource access for data exfiltration indicators, and correlates events across multiple components to identify attack campaigns.

Investigation happens conversationally. The MAD questions involved components about suspicious activity. It requests detailed logs from relevant timeframes. It compares observations across different MADs to build comprehensive understanding. This conversational investigation leverages ecosystem-wide visibility through the conversation bus.

Investigation findings drive response decisions. False positives are noted for future refinement—the MAD learns which patterns don't represent genuine threats. Confirmed threats trigger containment—affected sessions are terminated, compromised credentials are revoked, vulnerable configurations are corrected. Severe incidents trigger escalation to human security professionals.

### 4.5 Security Reviews

Beyond reactive monitoring and testing, the security operations MAD conducts proactive security reviews. It evaluates system configurations against security baselines, assesses new capabilities for security implications, reviews permission structures for excessive access, and validates encryption coverage for sensitive data.

These reviews happen automatically on regular schedules and when triggered by significant changes. New MAD deployments receive security review before production activation. Major configuration changes undergo security analysis. Regular comprehensive reviews ensure security posture doesn't degrade gradually through accumulated small changes.

Review findings become improvement recommendations. The security operations MAD creates conversations with relevant components, suggesting security enhancements. It may recommend additional encryption, suggest access restriction, propose monitoring improvements, or identify configuration hardening opportunities. These recommendations drive continuous security improvement.

***

## 5. Secrets Management: Credential Protection

### 5.1 The Secrets Challenge

Digital systems depend on secrets—API keys accessing external services, database passwords enabling data access, OAuth tokens authorizing on behalf of users, cryptographic keys protecting data, and signing keys verifying authenticity. These secrets enable capabilities but create security risks. Exposed secrets grant unauthorized access. Stolen credentials enable impersonation. Compromised keys undermine cryptographic protection.

Traditional secrets management burdens developers and operators. Secrets are embedded in configuration files, stored in environment variables, passed through insecure channels, and rarely rotated. This manual approach makes secrets management error-prone and security vulnerabilities common.

### 5.2 Centralized Secret Storage

The secrets management MAD provides centralized secure storage for all ecosystem secrets. API keys, passwords, tokens, and cryptographic keys are stored in encrypted vaults with access controls. Secrets never appear in configuration files, source code, or logs. They're requested conversationally when needed and provided only to authorized requesters.

Storage security combines encryption, access control, and audit logging. Secrets are encrypted at rest using keys managed by the cryptographic services MAD. Access requires authentication and authorization through the authentication MAD. Every secret access is logged for security audit. This layered protection ensures secrets remain confidential even if storage systems are compromised.

Secret organization reflects security boundaries. Different secret categories have different access policies. Infrastructure secrets might be accessible only to infrastructure MADs. User credentials are restricted to authentication components. API keys are available only to MADs requiring those specific integrations. This compartmentalization limits breach impact—compromising one component doesn't expose all secrets.

### 5.3 Automatic Secret Generation

Secret generation requires randomness and appropriate format. The secrets management MAD generates secrets automatically when new credentials are needed, ensuring adequate entropy, appropriate length, and correct format.

When a new API integration requires credentials, the MAD generates appropriately complex API keys. When database users need creation, the MAD generates cryptographically random passwords. When signing keys are needed, the MAD coordinates with the cryptographic services MAD to generate appropriate key pairs.

This automatic generation eliminates weak secrets. No human-chosen passwords, no predictable keys, no inadequate entropy. All secrets meet security requirements by default.

### 5.4 Secret Rotation

Credentials should rotate regularly—periodic changes limit breach windows and reduce compromise impact. The secrets management MAD implements automatic secret rotation on configurable schedules.

Rotation works differently for different secret types. Symmetric keys can rotate by generating new keys and re-encrypting data. API keys rotate by registering new keys with services before invalidating old keys. Database passwords rotate by creating new credentials and updating connection configurations. The MAD understands appropriate rotation approaches for each secret type.

Rotation happens transparently. MADs using secrets receive new credentials automatically without requiring code changes. Old credentials remain valid briefly during transition to ensure uninterrupted operation. Only after confirming new credentials work are old credentials revoked. This graceful rotation prevents service disruption while ensuring regular credential renewal.

### 5.5 Secret Revocation

When secrets are compromised or no longer needed, revocation prevents continued use. The secrets management MAD coordinates revocation across all relevant systems.

Revocation affects multiple layers. The secret is removed from secure storage preventing future requests. Services using the secret are notified to stop using it. External systems (for API keys and tokens) are informed of revocation. Audit logs capture revocation timing and reason. This comprehensive revocation ensures revoked secrets cannot enable access.

Emergency revocation handles security incidents rapidly. When compromise is detected, immediate revocation limits attacker access. The security operations MAD can trigger emergency revocation when investigation reveals credential compromise. Speed of revocation limits breach impact.

### 5.6 Conversational Secret Access

MADs access secrets conversationally without hardcoding credentials. A MAD requests "the API key for service X" and receives the current key. This conversational access enables transparency, access control, audit logging, and automatic rotation without requiring requesting MADs to implement secret management.

This approach makes secrets management automatic rather than administrative. Developers don't embed secrets in code. Operators don't manage secret files. MADs simply request needed credentials when needed. The secrets management MAD handles generation, storage, rotation, and revocation invisibly.

***

## 6. Security Domain Coordination

### 6.1 Layered Defense Integration

The four Security MADs implement defense-in-depth through coordinated operation. Identity verification by the authentication MAD determines who can access secrets from the secrets management MAD. Cryptographic protection by the cryptographic services MAD secures data that authentication and authorization regulate access to. Security monitoring by the security operations MAD detects when authentication is bypassed or secrets are compromised.

This coordination creates resilient security where weaknesses in one layer don't create complete vulnerabilities. Compromised credentials are detected through security monitoring. Authentication bypasses are limited by cryptographic protection of underlying data. Cryptographic vulnerabilities are mitigated through robust access controls. No single layer failure creates complete security breach.

### 6.2 Incident Response Coordination

Security incidents require coordinated response across Security MADs. The security operations MAD detects the anomaly and initiates investigation. The authentication MAD terminates affected sessions and requires re-authentication. The secrets management MAD rotates potentially compromised credentials. The cryptographic services MAD re-encrypts exposed data with new keys.

This coordinated response contains breaches rapidly. Multiple MADs act in concert to eliminate attacker access, protect data, and restore secure state. Response happens conversationally through the conversation bus, enabling rapid coordination without requiring centralized incident orchestration.

### 6.3 Security Policy Enforcement

Security policies apply uniformly across the ecosystem through Security MAD coordination. Authentication policies determine required verification factors. Authorization policies define role permissions. Encryption policies specify data protection requirements. Secret policies govern rotation schedules and access restrictions.

These policies are configured once in Security MADs and applied automatically everywhere. Other MADs don't implement security policies themselves—they request security services from Security MADs that enforce policies transparently. Policy changes propagate automatically to all components without requiring individual MAD updates.

***

## 7. Progressive Cognitive Pipeline Integration

### 7.1 Learning Security Patterns

As Security MADs operate, they learn patterns through the Progressive Cognitive Pipeline. The LPPM observes repeated security workflows and compiles them into optimized processes.

Common authentication flows become compilable patterns. Routine secret requests execute through learned processes. Standard security reviews follow compiled workflows. This learning makes security operations increasingly efficient while maintaining protection quality.

### 7.2 Optimizing Threat Detection

The security operations MAD improves threat detection through the CET and DTR. The CET optimizes context assembly for threat analysis—which historical patterns inform current anomaly assessment? The DTR learns which patterns represent genuine threats versus benign variations, reducing false positive rates.

This learning makes security monitoring progressively more accurate. Early operation might generate excessive alerts as patterns are learned. Mature operation focuses on genuine threats, reducing alert fatigue while maintaining comprehensive monitoring.

### 7.3 Adaptive Security

Security MADs adapt security controls to learned patterns. The authentication MAD learns typical user behavior and adjusts context-aware authentication accordingly. The security operations MAD learns normal system patterns and focuses monitoring on unusual deviations. This adaptive security provides protection proportional to actual risk rather than applying uniform controls regardless of context.

***

## 8. Current Implementation Status

*For complete implementation status and version progression details, see Paper J02: System Evolution and Current State.*

### 8.1 Authentication and Authorization MAD

The authentication and authorization MAD is operational at V1 with password authentication, JWT session management, and basic role-based access control. Multi-factor authentication works for high-security contexts. Session management handles token generation, validation, and invalidation.

Areas for enhancement include biometric authentication options, sophisticated context-aware security based on behavioral patterns, single sign-on integration with external identity providers, and fine-grained permission models beyond basic role definitions.

### 8.2 Cryptographic Services MAD

The cryptographic services MAD is operational at V1 providing encryption, decryption, and signature services. TLS certificates for external communication are managed automatically. Encryption at rest protects sensitive data. Key management handles generation, storage, and rotation.

Areas for enhancement include post-quantum cryptography preparation for quantum-resistant algorithms, hardware security module integration for cryptographic key protection, and automated certificate authority operation for internal PKI.

### 8.3 Security Operations MAD

The security operations MAD is operational at V1 with continuous monitoring of conversation bus activity. Basic anomaly detection identifies unusual patterns. Manual penetration testing is supported through eMAD composition, though automated regular testing is not yet implemented.

Areas for enhancement include sophisticated anomaly detection using machine learning, automated penetration testing on regular schedules, integration with external threat intelligence feeds, and automated incident response capabilities beyond human-coordinated responses.

### 8.4 Secrets Management MAD

The secrets management MAD is operational at V1 providing centralized secret storage with encryption and access control. Conversational secret access works reliably. Basic secret rotation is implemented for some credential types.

Areas for enhancement include comprehensive automatic rotation across all secret types, integration with external secret management services, emergency revocation workflows with automated breach response, and sophisticated audit capabilities for secret access patterns.

***

## 9. Conclusion

The Security domain demonstrates how the MAD pattern can implement sophisticated defense-in-depth security through specialized components coordinating to provide comprehensive protection. Four Security MADs cover essential security layers—identity, cryptography, threat detection, and credential management—while making robust security automatic and invisible.

This approach addresses a fundamental challenge in security: making robust protection simple enough that it's implemented correctly and consistently. When security requires constant expertise and attention, it becomes a burden that's often neglected or implemented incorrectly. When security MADs handle complexity automatically, robust protection becomes the default state.

The Security domain's coordination capabilities create resilient defense where no single layer failure creates complete vulnerability. Identity verification, cryptographic protection, continuous monitoring, and credential management work together, each mitigating weaknesses in others. This layered defense provides security greater than the sum of individual protections.

Perhaps most importantly, the Security domain embodies the principle that security should enable capability rather than creating barriers. Security MADs make robust protection invisible and automatic, allowing users and other MADs to focus on their objectives while security operates transparently. Complexity exists in Security MAD implementations, but that complexity is hidden behind simple conversational interfaces that make security both comprehensive and accessible.

***

## References

1.  Role-based access control patterns and identity management
2.  Cryptographic best practices and key management
3.  Security operations and threat detection methodologies
4.  Secrets management and credential lifecycle patterns
5.  Defense-in-depth security architecture principles

***

*Paper M06 - Draft v1.3 - October 17, 2025*
