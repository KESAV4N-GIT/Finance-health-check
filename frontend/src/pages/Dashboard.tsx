import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
    Box,
    Grid,
    Card,
    CardContent,
    Typography,
    CircularProgress,
    Tooltip,
    Chip,
} from '@mui/material'
import {
    TrendingUp,
    Receipt,
    Savings,
    ShowChart,
    Info,
} from '@mui/icons-material'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts'
import api from '../services/api'

interface FinancialSummary {
    total_revenue: number
    total_expenses: number
    net_profit: number
    profit_margin: number
    operating_cash_flow: number
    current_ratio: number | null
    debt_to_equity: number | null
    revenue_change: number | null
    expense_change: number | null
    profit_change: number | null
    health_score: number
    health_status: string
    period_label: string
}

export default function Dashboard() {
    const { t } = useTranslation()
    const [loading, setLoading] = useState(true)
    const [summary, setSummary] = useState<FinancialSummary | null>(null)
    const [cashFlowData, setCashFlowData] = useState<any[]>([])

    useEffect(() => {
        loadDashboardData()
    }, [])

    const loadDashboardData = async () => {
        try {
            const [summaryRes, cashFlowRes] = await Promise.all([
                api.get('/api/financial/summary'),
                api.get('/api/financial/cash-flow?periods=6'),
            ])
            setSummary(summaryRes.data)
            setCashFlowData(cashFlowRes.data.historical || [])
        } catch (error) {
            // Use mock data for demo
            setSummary({
                total_revenue: 1250000,
                total_expenses: 980000,
                net_profit: 270000,
                profit_margin: 21.6,
                operating_cash_flow: 185000,
                current_ratio: 1.85,
                debt_to_equity: 0.65,
                revenue_change: 15.3,
                expense_change: 8.2,
                profit_change: 28.5,
                health_score: 78,
                health_status: 'healthy',
                period_label: 'Jan 2026',
            })
            setCashFlowData([
                { period: 'Aug', net: 120000 },
                { period: 'Sep', net: 145000 },
                { period: 'Oct', net: 132000 },
                { period: 'Nov', net: 168000 },
                { period: 'Dec', net: 155000 },
                { period: 'Jan', net: 185000 },
            ])
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0,
        }).format(value)
    }

    const getHealthColor = (status: string) => {
        switch (status) {
            case 'healthy': return '#10b981'
            case 'caution': return '#f59e0b'
            case 'critical': return '#ef4444'
            default: return '#64748b'
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
                {t('dashboard')}
                <Chip
                    label={summary?.period_label}
                    size="small"
                    sx={{ ml: 2, fontWeight: 500 }}
                />
            </Typography>

            {/* Health Score Card */}
            <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%)', color: 'white' }}>
                <CardContent sx={{ p: 3 }}>
                    <Grid container alignItems="center" spacing={3}>
                        <Grid item xs={12} md={4}>
                            <Typography variant="h6" sx={{ opacity: 0.9, mb: 1 }}>
                                {t('financialHealth')}
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
                                <Typography variant="h2" fontWeight={700}>
                                    {summary?.health_score}
                                </Typography>
                                <Typography variant="h5">/100</Typography>
                            </Box>
                            <Chip
                                label={t(summary?.health_status || 'healthy')}
                                sx={{
                                    mt: 1,
                                    bgcolor: getHealthColor(summary?.health_status || ''),
                                    color: 'white',
                                    fontWeight: 600,
                                }}
                            />
                        </Grid>
                        <Grid item xs={12} md={8}>
                            <ResponsiveContainer width="100%" height={120}>
                                <LineChart data={cashFlowData}>
                                    <Line
                                        type="monotone"
                                        dataKey="net"
                                        stroke="white"
                                        strokeWidth={3}
                                        dot={false}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            {/* Metric Cards */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card className="card-hover">
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                <Box sx={{ p: 1, borderRadius: 2, bgcolor: 'primary.light', color: 'white' }}>
                                    <TrendingUp />
                                </Box>
                                {summary?.revenue_change !== null && (
                                    <Chip
                                        size="small"
                                        label={`${summary.revenue_change > 0 ? '+' : ''}${summary.revenue_change?.toFixed(1)}%`}
                                        color={summary.revenue_change > 0 ? 'success' : 'error'}
                                    />
                                )}
                            </Box>
                            <Typography color="text.secondary" variant="body2">
                                {t('revenue')}
                            </Typography>
                            <Typography variant="h5" fontWeight={700}>
                                {formatCurrency(summary?.total_revenue || 0)}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Card className="card-hover">
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                <Box sx={{ p: 1, borderRadius: 2, bgcolor: 'error.light', color: 'white' }}>
                                    <Receipt />
                                </Box>
                                {summary?.expense_change !== null && (
                                    <Chip
                                        size="small"
                                        label={`${summary.expense_change > 0 ? '+' : ''}${summary.expense_change?.toFixed(1)}%`}
                                        color={summary.expense_change < 0 ? 'success' : 'warning'}
                                    />
                                )}
                            </Box>
                            <Typography color="text.secondary" variant="body2">
                                {t('expenses')}
                            </Typography>
                            <Typography variant="h5" fontWeight={700}>
                                {formatCurrency(summary?.total_expenses || 0)}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Card className="card-hover">
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                <Box sx={{ p: 1, borderRadius: 2, bgcolor: 'success.light', color: 'white' }}>
                                    <Savings />
                                </Box>
                                {summary?.profit_change !== null && (
                                    <Chip
                                        size="small"
                                        label={`${summary.profit_change > 0 ? '+' : ''}${summary.profit_change?.toFixed(1)}%`}
                                        color={summary.profit_change > 0 ? 'success' : 'error'}
                                    />
                                )}
                            </Box>
                            <Typography color="text.secondary" variant="body2">
                                {t('netProfit')}
                            </Typography>
                            <Typography variant="h5" fontWeight={700}>
                                {formatCurrency(summary?.net_profit || 0)}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Card className="card-hover">
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                <Box sx={{ p: 1, borderRadius: 2, bgcolor: 'secondary.light', color: 'white' }}>
                                    <ShowChart />
                                </Box>
                            </Box>
                            <Typography color="text.secondary" variant="body2">
                                {t('cashFlow')}
                            </Typography>
                            <Typography variant="h5" fontWeight={700}>
                                {formatCurrency(summary?.operating_cash_flow || 0)}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Charts Row */}
            <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                                Cash Flow Trend
                            </Typography>
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={cashFlowData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="period" />
                                    <YAxis tickFormatter={(v: number) => `₹${(v / 1000).toFixed(0)}K`} />
                                    <RechartsTooltip formatter={(value: number) => formatCurrency(value)} />
                                    <Line
                                        type="monotone"
                                        dataKey="net"
                                        stroke="#2563eb"
                                        strokeWidth={3}
                                        dot={{ fill: '#2563eb', strokeWidth: 2 }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                                Key Ratios
                                <Tooltip title={t('currentRatioTooltip')}>
                                    <Info sx={{ fontSize: 16, ml: 1, color: 'text.secondary', cursor: 'help' }} />
                                </Tooltip>
                            </Typography>
                            <Box sx={{ mb: 3 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography color="text.secondary">Current Ratio</Typography>
                                    <Typography fontWeight={600}>
                                        {summary?.current_ratio?.toFixed(2) || 'N/A'}
                                    </Typography>
                                </Box>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography color="text.secondary">Debt/Equity</Typography>
                                    <Typography fontWeight={600}>
                                        {summary?.debt_to_equity?.toFixed(2) || 'N/A'}
                                    </Typography>
                                </Box>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography color="text.secondary">Profit Margin</Typography>
                                    <Typography fontWeight={600}>
                                        {summary?.profit_margin?.toFixed(1)}%
                                    </Typography>
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    )
}
