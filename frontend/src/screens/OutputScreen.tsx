/**
 * INTENTA — Output Screen
 * Displays all 14 sections of the generated enterprise design.
 */
import React, { useRef, useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Animated,
  StatusBar,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RouteProp } from '@react-navigation/native';
import { RootStackParamList } from '../navigation/AppNavigator';
import ResultCard, { InfoRow, TagList, BulletList } from '../components/ResultCard';
import { theme } from '../theme/theme';
import { jsPDF } from 'jspdf';
import { getCurrentUser } from '../services/localAuth';

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Output'>;
  route: RouteProp<RootStackParamList, 'Output'>;
};

const RISK_COLORS: Record<string, string> = {
  low: theme.colors.success,
  medium: theme.colors.warning,
  high: theme.colors.error,
  critical: theme.colors.status.critical,
};

const PRIORITY_COLORS: Record<string, string> = {
  critical: theme.colors.status.critical,
  high: theme.colors.status.high,
  medium: theme.colors.status.medium,
};

export default function OutputScreen({ navigation, route }: Props) {
  const { result, processingMs } = route.params;
  const { intent, architecture, tech_stack, code_blueprint, validation, compliance, governance, explainability } = result;

  const headerOpacity = useRef(new Animated.Value(0)).current;
  const headerTranslate = useRef(new Animated.Value(-10)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(headerOpacity, { toValue: 1, duration: 500, useNativeDriver: true }),
      Animated.timing(headerTranslate, { toValue: 0, duration: 500, useNativeDriver: true }),
    ]).start();
  }, []);

  const confidencePct = Math.round(explainability.confidence_score * 100);

  const [isPrinting, setIsPrinting] = useState(false);

  const downloadJSON = () => {
    if (Platform.OS === 'web') {
      const jsonString = JSON.stringify(result, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `intenta_design_${result.session_id.slice(0, 8)}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const downloadPDF = async () => {
    if (Platform.OS === 'web') {
      setIsPrinting(true);
      try {
        const doc = new jsPDF('p', 'mm', 'a4');
        let y = 20;
        const margin = 15;
        const pageWidth = doc.internal.pageSize.getWidth();
        const maxLineWidth = pageWidth - margin * 2;
        const pageHeight = doc.internal.pageSize.getHeight();
        let pageNum = 1;
        
        const renderFooter = () => {
          doc.setFont("helvetica", "normal");
          doc.setFontSize(9);
          doc.setTextColor(150, 150, 150);
          const userEmail = getCurrentUser()?.email || 'user@intenta.local';
          const footerStr = `INTENTA AI Architecture - Generated for ${userEmail}`;
          doc.text(footerStr, margin, pageHeight - 12);
          const pageStr = `Page ${pageNum}`;
          doc.text(pageStr, pageWidth - margin - doc.getTextWidth(pageStr), pageHeight - 12);
        };

        const checkPage = (addedHeight: number) => {
          if (y + addedHeight >= pageHeight - 20) {
            renderFooter();
            doc.addPage();
            pageNum++;
            y = 20;
          }
        };

        const addTitle = (title: string) => {
          checkPage(15);
          if (y > 35) y += 5; // Extra padding if not at top of page (below header)
          doc.setFillColor(245, 245, 250); // Light purple/blue background
          doc.rect(margin, y - 5, pageWidth - margin * 2, 9, 'F');
          
          doc.setFont("helvetica", "bold");
          doc.setFontSize(12);
          doc.setTextColor(79, 70, 229); // INTENTA Primary brand color
          doc.text(title, margin + 2, y + 1);
          y += 7; // Reduced gap between title and text
        };

        const addText = (text: string, indent = 0, color = [60, 60, 60], isBold = false) => {
          if (!text) return;
          doc.setFont("helvetica", isBold ? "bold" : "normal");
          doc.setFontSize(10);
          doc.setTextColor(color[0], color[1], color[2]);
          const lines = doc.splitTextToSize(text, maxLineWidth - indent);
          checkPage(lines.length * 5);
          doc.text(lines, margin + indent, y);
          y += lines.length * 5 + 1; // Tighter line-height to reduce gaps
        };

        const addKeyValue = (key: string, value: string) => {
          if (!value) return;
          checkPage(6);
          doc.setFont("helvetica", "bold");
          doc.setFontSize(10);
          doc.setTextColor(40, 40, 40);
          const keyStr = `${key}: `;
          doc.text(keyStr, margin, y);
          
          const keyWidth = doc.getTextWidth(keyStr);
          doc.setFont("helvetica", "normal");
          doc.setTextColor(80, 80, 80);
          const lines = doc.splitTextToSize(value, maxLineWidth - keyWidth);
          checkPage(lines.length * 5);
          doc.text(lines, margin + keyWidth, y);
          y += lines.length * 5 + 1;
        };
        
        // ── Document Cover / Setup ──
        doc.setFillColor(15, 23, 42); // Dark header bar
        doc.rect(0, 0, pageWidth, 25, 'F');
        doc.setFontSize(22);
        doc.setFont("helvetica", "bold");
        doc.setTextColor(255, 255, 255);
        doc.text("INTENTA Enterprise System Design", margin, 17);
        
        y = 32; // Start tighter below the giant header
        
        // 1. Overview
        addTitle("1. System Overview");
        addKeyValue("Domain Strategy", result.intent.domain.toUpperCase());
        addKeyValue("Intended Scale", result.intent.scale.toUpperCase());
        addKeyValue("Core Goal", result.intent.goal);
        
        // 2. Architecture
        addTitle("2. Architecture Design");
        addKeyValue("Pattern", result.architecture.pattern);
        addKeyValue("Communication", result.code_blueprint.communication_style);
        addText("Core Services:", 0, [40,40,40], true);
        (result.architecture.services || []).forEach(s => addText(`• ${s}`, 5));
        addText("Strategic Rationale:", 0, [40,40,40], true);
        addText(result.architecture.rationale);
        
        // 3. Data Model
        addTitle("3. Data Model & Storage");
        addText(result.code_blueprint.data_model || "Relational schema structured around core domain entities.");
        addText("Databases & Cache Technologies:", 0, [40,40,40], true);
        (result.tech_stack.database || []).forEach(d => addText(`• ${d}`, 5));
        
        // 4. APIs
        addTitle("4. API Specifications");
        addText("Communication Format:", 0, [40,40,40], true);
        (result.code_blueprint.api_specifications || []).forEach(f => addText(`• ${f}`, 5));
        addText("Service Contracts:", 0, [40,40,40], true);
        (result.code_blueprint.services || []).forEach(svc => {
          addText(`Service: ${svc.name}`, 3, [40,40,40], true);
          (svc.endpoints || []).forEach(ep => addText(`-  ${ep}`, 7));
        });

        // 5. Security
        addTitle("5. Security Framework");
        addText(result.compliance.security_framework || "Zero Trust Architecture with strict RBAC/ABAC boundary limits.");
        addText("Encryption Requirements:", 0, [40,40,40], true);
        (result.compliance.encryption_requirements || []).forEach(r => addText(`• ${r}`, 5));

        // 6. Compliance
        addTitle("6. Compliance Requirements");
        if (result.compliance.overview_text) addText(result.compliance.overview_text);
        addText("Applicable Regulations:", 0, [40,40,40], true);
        (result.compliance.applicable_regulations || []).forEach(r => addText(`• ${r}`, 5));
        
        // 7. Governance
        addTitle("7. Governance Model");
        addText("Defined RBAC Roles:", 0, [40,40,40], true);
        (result.governance.rbac_roles || []).forEach(role => {
           addText(`[${role.role.toUpperCase()}]`, 3, [124, 58, 237], true); // Purple roles
           addText(`${role.description}`, 5);
        });

        // 8. Roadmap
        addTitle("8. Development Roadmap");
        if (typeof result.governance.development_roadmap === 'string') {
          addText(result.governance.development_roadmap);
        } else {
          (result.governance.development_roadmap || []).forEach(r => addText(`• ${r}`, 5));
        }

        // 9. Testing
        addTitle("9. Testing Strategy");
        addText("Unit Validation Sequence:", 0, [40,40,40], true);
        (result.validation.unit_tests || []).forEach(t => addText(`• ${t}`, 5));
        addText("Integration & Automated End-to-End:", 0, [40,40,40], true);
        [...(result.validation.integration_tests || []), ...(result.validation.e2e_tests || [])].forEach(t => addText(`• ${t}`, 5));

        // 10. Deployment
        addTitle("10. Deployment Plan");
        addText(result.tech_stack.deployment_plan || "Standard CI/CD automated deployment.");
        addText("Infrastructure Topologies:", 0, [40,40,40], true);
        (result.tech_stack.infrastructure || []).forEach(i => addText(`• ${i}`, 5));

        // 11. Monitoring
        addTitle("11. Monitoring & Observability");
        addText("Instrumentation Tooling:", 0, [40,40,40], true);
        (result.tech_stack.monitoring_observability || ["Prometheus", "Grafana"]).forEach(t => addText(`• ${t}`, 5));
        addText("Mandatory Audit Events:", 0, [40,40,40], true);
        (result.compliance.audit_log_events || []).forEach(l => addText(`• ${l}`, 5));

        // 12. Risk
        addTitle("12. Risk Assessment");
        addText(`Confidence Score: ${Math.round(result.explainability.confidence_score * 100)}%`, 0, [40, 40, 40], true);
        addText(result.explainability.overall_risk_summary);
        
        addText("Decision Factors:", 0, [40,40,40], true);
        (result.explainability.decisions || []).forEach(d => {
          const color = d.risk_level.toLowerCase() === 'high' ? [239, 68, 68] : [234, 179, 8];
          addText(`${d.decision.toUpperCase()}`, 3, color as number[], true);
          addText(`${d.rationale}`, 5);
        });

        // 13. Cost
        addTitle("13. Cost Estimation");
        addText(result.explainability.cost_estimation || "Cloud agnostic baseline with moderate expected cost overhead based on geographic scale.");

        // 14. Documentation
        addTitle("14. Documentation Strategy");
        addText(result.governance.documentation_plan || "Maintain updated Architecture Decision Records (ADRs) alongside swagger definitions.");
        
        // Final Footer on last page
        renderFooter();

        doc.save(`intenta_design_${result.session_id.slice(0, 8)}.pdf`);
        
      } catch (error) {
        console.error("PDF Generation Error", error);
      } finally {
        setIsPrinting(false);
      }
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" />

      {/* Sticky header */}
      <LinearGradient colors={['#0A0A1A', '#11112B']} style={styles.stickyHeader}>
        <TouchableOpacity onPress={() => navigation.navigate('Input')} style={styles.backButton}>
          <Text style={styles.backText}>← New Design</Text>
        </TouchableOpacity>
        
        <View style={styles.headerCenter}>
          <Text style={styles.headerTitle}>INTENTA Output</Text>
          <Text style={styles.headerSub}>{Math.round(processingMs / 1000)}s processing · {result.session_id.slice(0, 8)}</Text>
        </View>

        <View style={styles.actionsContainer}>
          <TouchableOpacity onPress={downloadPDF} style={styles.actionBtn} activeOpacity={0.8}>
            <Text style={{ fontSize: 16, color: '#000', fontWeight: '800' }}>↓</Text>
            <Text style={styles.actionBtnText}>PDF</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={downloadJSON} style={styles.actionBtn} activeOpacity={0.8}>
            <Text style={{ fontSize: 16, color: '#000', fontWeight: '800' }}>↓</Text>
            <Text style={styles.actionBtnText}>JSON</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View nativeID="pdf-content-wrapper" style={{ flex: 1, backgroundColor: theme.colors.bg.primary }}>
        {/* ─── 1. System Overview ─────────────────────────────── */}
        <Animated.View style={[styles.heroCard, { opacity: headerOpacity, transform: [{ translateY: headerTranslate }] }]}>
          <ResultCard title="System Overview" icon="🏗" accentColor="#4F46E5" defaultExpanded forceExpanded={isPrinting}>
            <Text style={styles.heroGoal}>{intent.goal}</Text>
            <View style={styles.heroMeta}>
              <Text style={styles.heroMetaItem}>🏢 {intent.domain.toUpperCase()}</Text>
              <Text style={styles.heroMetaDot}>·</Text>
              <Text style={styles.heroMetaItem}>📈 {intent.scale.toUpperCase()}</Text>
              <Text style={styles.heroMetaDot}>·</Text>
              <Text style={styles.heroMetaItem}>🏗 {architecture.pattern}</Text>
            </View>
            <Text style={styles.sectionLabel}>Tech Stack Selection</Text>
            <Text style={styles.bodyText}>{tech_stack.rationale}</Text>
          </ResultCard>
        </Animated.View>

        {/* ─── 2. Architecture Design ─────────────────────────── */}
        <ResultCard title="Architecture Design" icon="🔗" accentColor="#7C3AED" badge={architecture.pattern} forceExpanded={isPrinting}>
          <InfoRow label="Pattern" value={architecture.pattern} accent="#A78BFA" />
          <InfoRow label="Communication" value={code_blueprint.communication_style} />
          <InfoRow label="API Gateway" value={code_blueprint.api_gateway} />
          <Text style={styles.sectionLabel}>Services</Text>
          <TagList tags={architecture.services || []} color="#7C3AED" />
          <Text style={styles.sectionLabel}>Rationale</Text>
          <Text style={styles.bodyText}>{architecture.rationale}</Text>
          <Text style={styles.sectionLabel}>Diagram</Text>
          <View style={styles.diagramBox}>
            <Text style={styles.diagramText}>{architecture.diagram_hint}</Text>
          </View>
        </ResultCard>

        {/* ─── 3. Data Model ──────────────────────────────────── */}
        <ResultCard title="Data Model" icon="📊" accentColor="#06B6D4" forceExpanded={isPrinting}>
          <Text style={styles.bodyText}>{code_blueprint.data_model || "Relational schema structured around core domain entities."}</Text>
          <Text style={styles.sectionLabel}>Databases Used</Text>
          <TagList tags={tech_stack.database || []} color="#06B6D4" />
        </ResultCard>

        {/* ─── 4. API Specifications ──────────────────────────── */}
        <ResultCard title="API Specifications" icon="🔌" accentColor="#22D3EE" forceExpanded={isPrinting}>
          <Text style={styles.sectionLabel}>API Format</Text>
          <BulletList items={code_blueprint.api_specifications || []} color="#22D3EE" />
          
          <Text style={styles.sectionLabel}>Service Endpoints</Text>
          {(code_blueprint.services || []).map((svc, i) => (
            <View key={i} style={styles.serviceCard}>
              <Text style={styles.serviceName}>▸ {svc.name}</Text>
              {(svc.endpoints || []).map((ep, j) => (
                <Text key={j} style={styles.endpoint}>{ep}</Text>
              ))}
            </View>
          ))}
        </ResultCard>

        {/* ─── 5. Security Framework ──────────────────────────── */}
        <ResultCard title="Security Framework" icon="🔐" accentColor="#F59E0B" forceExpanded={isPrinting}>
          <Text style={styles.bodyText}>{compliance.security_framework || "Zero Trust Architecture with strict RBAC/ABAC limits."}</Text>
          <Text style={styles.sectionLabel}>Encryption Requirements</Text>
          <BulletList items={compliance.encryption_requirements || []} color="#F59E0B" />
        </ResultCard>

        {/* ─── 6. Compliance Requirements ─────────────────────── */}
        <ResultCard title="Compliance Requirements" icon="⚖️" accentColor="#F72585" badge={`${compliance.rules?.length || 0} rules`} forceExpanded={isPrinting}>
          {compliance.overview_text ? <Text style={[styles.bodyText, {marginBottom: 10}]}>{compliance.overview_text}</Text> : null}
          <Text style={styles.sectionLabel}>Regulations</Text>
          <TagList tags={compliance.applicable_regulations || []} color="#F72585" />
          <Text style={styles.sectionLabel}>Data Classification</Text>
          {Object.entries(compliance.data_classification || {}).map(([field, cls]) => (
            <InfoRow key={field} label={field} value={cls as string} />
          ))}
        </ResultCard>

        {/* ─── 7. Governance Model ────────────────────────────── */}
        <ResultCard title="Governance Model" icon="📋" accentColor="#EAB308" forceExpanded={isPrinting}>
          <Text style={styles.sectionLabel}>Roles</Text>
          {(governance.rbac_roles || []).map((role, i) => (
            <View key={i} style={styles.roleCard}>
              <View style={styles.roleHeader}>
                <Text style={styles.roleName}>{role.role}</Text>
              </View>
              <Text style={styles.roleDesc}>{role.description}</Text>
            </View>
          ))}
          <Text style={styles.sectionLabel}>Workflows</Text>
          {governance.approval_workflows.map((wf, i) => (
            <View key={i} style={styles.workflowCard}>
              <Text style={styles.workflowName}>{wf.name}</Text>
              <Text style={styles.workflowSla}>SLA: {wf.sla_hours}h</Text>
            </View>
          ))}
        </ResultCard>

        {/* ─── 8. Development Roadmap ─────────────────────────── */}
        <ResultCard title="Development Roadmap" icon="🗺️" accentColor="#10B981" forceExpanded={isPrinting}>
          {typeof governance.development_roadmap === 'string' ? (
            <Text style={styles.bodyText}>{governance.development_roadmap}</Text>
          ) : (
            <BulletList items={governance.development_roadmap || ["Phase 1: MVP", "Phase 2: Scale"]} color="#10B981" />
          )}
        </ResultCard>

        {/* ─── 9. Testing Strategy ────────────────────────────── */}
        <ResultCard title="Testing Strategy" icon="✅" accentColor="#34D399" forceExpanded={isPrinting}>
          <Text style={styles.sectionLabel}>Unit Tests</Text>
          <BulletList items={validation.unit_tests || []} color="#10B981" />
          <Text style={styles.sectionLabel}>Integration & E2E</Text>
          <BulletList items={[...(validation.integration_tests || []), ...(validation.e2e_tests || [])]} color="#34D399" />
        </ResultCard>

        {/* ─── 10. Deployment Plan ────────────────────────────── */}
        <ResultCard title="Deployment Plan" icon="🚀" accentColor="#0EA5E9" forceExpanded={isPrinting}>
          <Text style={styles.bodyText}>{tech_stack.deployment_plan || "Standard CI/CD automated deployment."}</Text>
          <Text style={styles.sectionLabel}>Infrastructure Elements</Text>
          <TagList tags={tech_stack.infrastructure || []} color="#0EA5E9" />
        </ResultCard>

        {/* ─── 11. Monitoring & Observability ─────────────────── */}
        <ResultCard title="Monitoring & Observability" icon="📈" accentColor="#6366F1" forceExpanded={isPrinting}>
          <Text style={styles.sectionLabel}>Tools</Text>
          <TagList tags={tech_stack.monitoring_observability || ["Prometheus", "Grafana"]} color="#6366F1" />
          <Text style={styles.sectionLabel}>Audit Logs</Text>
          <TagList tags={compliance.audit_log_events || []} color="#818CF8" />
        </ResultCard>

        {/* ─── 12. Risk Assessment ────────────────────────────── */}
        <ResultCard title="Risk Assessment" icon="⚠️" accentColor="#EF4444" badge={`${confidencePct}% confidence`} forceExpanded={isPrinting}>
          <Text style={styles.bodyText}>{explainability.overall_risk_summary}</Text>
          {(explainability.decisions || []).map((d, i) => (
            <View key={i} style={styles.decisionCard}>
              <View style={styles.decisionHeader}>
                <Text style={styles.decisionTitle}>{d.decision}</Text>
                <Text style={[styles.riskBadge, { color: RISK_COLORS[d.risk_level] || theme.colors.warning }]}>
                  {d.risk_level.toUpperCase()} RISK
                </Text>
              </View>
              <Text style={styles.decisionRationale}>{d.rationale}</Text>
            </View>
          ))}
        </ResultCard>

        {/* ─── 13. Cost Estimation ────────────────────────────── */}
        <ResultCard title="Cost Estimation" icon="💰" accentColor="#22C55E" forceExpanded={isPrinting}>
          <Text style={styles.bodyText}>{explainability.cost_estimation || "Cloud agnostic baseline with moderate expected cost overhead based on scale."}</Text>
        </ResultCard>

        {/* ─── 14. Documentation ──────────────────────────────── */}
        <ResultCard title="Documentation" icon="📚" accentColor="#8B5CF6" forceExpanded={isPrinting}>
          <Text style={styles.bodyText}>{governance.documentation_plan || "Maintain updated Architecture Decision Records (ADRs) alongside swagger definitions."}</Text>
        </ResultCard>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Generated by INTENTA SuperAgent · Session {result.session_id.slice(0, 8)}
          </Text>
          {!isPrinting && (
            <TouchableOpacity onPress={() => navigation.navigate('Input')}>
              <LinearGradient colors={['#7C3AED', '#4F46E5']} style={styles.footerButton}>
                <Text style={styles.footerButtonText}>✦  Generate Another Design</Text>
              </LinearGradient>
            </TouchableOpacity>
          )}
        </View>
        </View>
      </ScrollView>

      {/* Print styles for window.print fallback just in case */}
      {Platform.OS === 'web' && (
        <style dangerouslySetInnerHTML={{__html: `
          @media print {
            .css-view-175hal2 { 
               display: none !important; /* Hide sticky header in print */
            }
            body { 
               background: #fff; 
               color: #000;
            }
          }
        `}} />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.bg.primary },
  stickyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 52,
    paddingBottom: 16,
    paddingHorizontal: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border.subtle,
  },
  backButton: { marginRight: theme.spacing.sm },
  backText: { color: theme.colors.brand.primary, fontSize: 14, fontWeight: '600' },
  headerCenter: { flex: 1, alignItems: 'center' },
  headerTitle: { color: theme.colors.text.primary, fontSize: 16, fontWeight: '700' },
  headerSub: { color: theme.colors.text.muted, fontSize: 11, marginTop: 2 },
  
  actionsContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  actionBtn: {
    backgroundColor: '#F3F4F6',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    gap: 4,
  },
  actionBtnText: {
    color: '#000',
    fontSize: 12,
    fontWeight: '600',
  },

  scroll: { flex: 1 },
  scrollContent: { padding: theme.spacing.md, paddingBottom: 60 },
  heroCard: { marginBottom: theme.spacing.md, borderRadius: theme.radii.lg, overflow: 'hidden' },
  heroGoal: { color: theme.colors.text.primary, fontSize: 17, fontWeight: '700', lineHeight: 24, marginBottom: theme.spacing.sm },
  heroMeta: { flexDirection: 'row', alignItems: 'center', marginBottom: theme.spacing.sm, flexWrap: 'wrap' },
  heroMetaItem: { color: theme.colors.brand.accent, fontSize: 12, fontWeight: '600' },
  heroMetaDot: { color: theme.colors.text.muted, marginHorizontal: 8 },
  sectionLabel: { color: theme.colors.text.muted, fontSize: 11, fontWeight: '700', letterSpacing: 1, textTransform: 'uppercase', marginTop: theme.spacing.md, marginBottom: theme.spacing.xs },
  bodyText: { color: theme.colors.text.secondary, fontSize: 13, lineHeight: 20 },
  diagramBox: { backgroundColor: 'rgba(0,0,0,0.3)', borderRadius: theme.radii.sm, padding: theme.spacing.sm, borderWidth: 1, borderColor: theme.colors.border.subtle },
  diagramText: { color: '#A78BFA', fontSize: 12, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' },
  serviceCard: { backgroundColor: 'rgba(6,182,212,0.07)', borderRadius: theme.radii.md, padding: theme.spacing.md, marginBottom: theme.spacing.sm, borderWidth: 1, borderColor: 'rgba(6,182,212,0.2)' },
  serviceName: { color: '#22D3EE', fontSize: 14, fontWeight: '700', marginBottom: 4 },
  endpoint: { color: '#67E8F9', fontSize: 12, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace', marginBottom: 2 },
  roleCard: { backgroundColor: 'rgba(234,179,8,0.08)', borderRadius: theme.radii.sm, padding: theme.spacing.sm, marginBottom: theme.spacing.sm, borderWidth: 1, borderColor: 'rgba(234,179,8,0.2)' },
  roleHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  roleName: { color: '#FDE047', fontSize: 13, fontWeight: '700' },
  roleDesc: { color: theme.colors.text.secondary, fontSize: 12 },
  workflowCard: { backgroundColor: 'rgba(234,179,8,0.05)', borderRadius: theme.radii.sm, padding: theme.spacing.sm, marginBottom: theme.spacing.sm, borderLeftWidth: 3, borderLeftColor: '#EAB308' },
  workflowName: { color: '#FDE047', fontSize: 13, fontWeight: '700', marginBottom: 2 },
  workflowSla: { color: theme.colors.text.muted, fontSize: 11, marginBottom: theme.spacing.xs },
  decisionCard: { backgroundColor: 'rgba(239,68,68,0.08)', borderRadius: theme.radii.md, padding: theme.spacing.md, marginBottom: theme.spacing.sm, borderWidth: 1, borderColor: 'rgba(239,68,68,0.2)' },
  decisionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: theme.spacing.xs },
  decisionTitle: { flex: 1, color: theme.colors.text.primary, fontSize: 13, fontWeight: '700', marginRight: theme.spacing.sm },
  riskBadge: { fontSize: 10, fontWeight: '800', letterSpacing: 0.5 },
  decisionRationale: { color: theme.colors.text.secondary, fontSize: 12, lineHeight: 18, marginBottom: theme.spacing.xs },
  footer: { marginTop: theme.spacing.lg, alignItems: 'center' },
  footerText: { color: theme.colors.text.muted, fontSize: 12, marginBottom: theme.spacing.md },
  footerButton: { paddingHorizontal: 32, paddingVertical: 16, borderRadius: theme.radii.full },
  footerButtonText: { color: '#FFFFFF', fontSize: 15, fontWeight: '700' },
});
