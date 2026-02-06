import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
    Box,
    Grid,
    Card,
    CardContent,
    Typography,
    CircularProgress,
    Chip,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
} from '@mui/material'
import { Warning, Error, CheckCircle, TrendingDown, TrendingUp } from '@mui/icons-material'
// Recharts can be used for pie charts if needed
import api from '../services/api'



export default function RiskAssessment() {
    const { t } = useTranslation()
    const [loading, setLoading] = useState(true)
    const [riskData, setRiskData] = useState<any>(null)

    useEffect(() => {
        loadRiskData()
    }, [])

    const loadRiskData = async () => {
        try {
            const response = await api.get('/api/analysis/risk')
            setRiskData(response.data)
        } catch {
            // Mock data
            setRiskData({
                overall_score: 45,
                liquidity_score: 38,
                solvency_score: 52,
                operational_score: 41,
                creditworthiness_score: 72,
                risk_level: 'medium',
                risk_factors: [
                    { name: 'Low Current Ratio', severity: 'high', description: 'Current assets below short-term obligations' },
                    { name: 'High Receivables', severity: 'medium', description: 'Days receivable above industry average' },
                    { name: 'Seasonal Revenue', severity: 'low', description: 'Revenue concentration in specific quarters' },
                ],
                recommendations: [
                    { title: 'Improve Collection', priority: 'high', description: 'Reduce accounts receivable days' },
                    { title: 'Build Cash Reserve', priority: 'medium', description: 'Maintain 3-month operating expenses' },
                ]
            })
        } finally {
            setLoading(false)
        }
    }

    const getRiskColor = (level: string) => {
        switch (level) {
            case 'low': return '#10b981'
            case 'medium': return '#f59e0b'
            case 'high': return '#ef4444'
            case 'critical': return '#dc2626'
            default: return '#64748b'
        }
    }

    const getSeverityIcon = (severity: string) => {
        switch (severity) {
            case 'low': return <CheckCircle color="success" />
            case 'medium': return <Warning color="warning" />
            case 'high': return <Error color="error" />
            default: return <Warning />
        }
    }

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
                <CircularProgress />
            </Box>
        )
    }



    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" fontWeight={700} sx={{ mb: 3 }}>
                {t('riskAssessment')}
            </Typography>

            <Grid container spacing={3}>
                {/* Overall Risk Score */}
                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center', py: 4 }}>
                            <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                                {t('overallRisk')}
                            </Typography>
                            <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                                <CircularProgress
                                    variant="determinate"
                                    value={riskData?.overall_score || 0}
                                    size={160}
                                    thickness={8}
                                    sx={{ color: getRiskColor(riskData?.risk_level) }}
                                />
                                <Box
                                    sx={{
                                        position: 'absolute',
                                        top: 0, left: 0, bottom: 0, right: 0,
                                        display: 'flex', flexDirection: 'column',
                                        alignItems: 'center', justifyContent: 'center',
                                    }}
                                >
                                    <Typography variant="h3" fontWeight={700}>
                                        {riskData?.overall_score}
                                    </Typography>
                                    <Chip
                                        label={t(riskData?.risk_level)}
                                        size="small"
                                        sx={{ bgcolor: getRiskColor(riskData?.risk_level), color: 'white', fontWeight: 600 }}
                                    />
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Risk Components */}
                <Grid item xs={12} md={8}>
                    <Card sx={{ height: '100%' }}>
                        <CardContent>
                            <Typography variant="h6" fontWeight={600} sx={{ mb: 3 }}>
                                Risk Components
                            </Typography>
                            <Grid container spacing={2}>
                                {[
                                    { label: t('liquidityRisk'), value: riskData?.liquidity_score },
                                    { label: t('solvencyRisk'), value: riskData?.solvency_score },
                                    { label: t('operationalRisk'), value: riskData?.operational_score },
                                    { label: 'Creditworthiness', value: riskData?.creditworthiness_score, inverse: true },
                                ].map((item, idx) => (
                                    <Grid item xs={6} key={idx}>
                                        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default' }}>
                                            <Typography variant="body2" color="text.secondary">
                                                {item.label}
                                            </Typography>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                <Typography variant="h5" fontWeight={700}>
                                                    {item.value}
                                                </Typography>
                                                {item.inverse ? (
                                                    <TrendingUp color="success" fontSize="small" />
                                                ) : item.value > 50 ? (
                                                    <TrendingDown color="error" fontSize="small" />
                                                ) : (
                                                    <TrendingUp color="success" fontSize="small" />
                                                )}
                                            </Box>
                                        </Box>
                                    </Grid>
                                ))}
                            </Grid>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Risk Factors */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                                Identified Risk Factors
                            </Typography>
                            <List>
                                {riskData?.risk_factors?.map((factor: any, idx: number) => (
                                    <ListItem key={idx} divider={idx < riskData.risk_factors.length - 1}>
                                        <ListItemIcon>
                                            {getSeverityIcon(factor.severity)}
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={factor.name}
                                            secondary={factor.description}
                                        />
                                        <Chip
                                            size="small"
                                            label={factor.severity}
                                            sx={{ bgcolor: getRiskColor(factor.severity), color: 'white' }}
                                        />
                                    </ListItem>
                                ))}
                            </List>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Recommendations */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                                Recommendations
                            </Typography>
                            <List>
                                {riskData?.recommendations?.map((rec: any, idx: number) => (
                                    <ListItem key={idx} divider={idx < riskData.recommendations.length - 1}>
                                        <ListItemText
                                            primary={rec.title}
                                            secondary={rec.description}
                                        />
                                        <Chip
                                            size="small"
                                            label={rec.priority}
                                            color={rec.priority === 'high' ? 'error' : rec.priority === 'medium' ? 'warning' : 'success'}
                                        />
                                    </ListItem>
                                ))}
                            </List>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    )
}
