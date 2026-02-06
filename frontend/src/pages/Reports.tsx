import { useState, useEffect } from 'react'
import {
    Box,
    Grid,
    Card,
    CardContent,
    Typography,
    Button,
    CircularProgress,
    Chip,
    List,
    ListItem,
    ListItemText,
    ListItemSecondaryAction,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
} from '@mui/material'
import { Add, Download, Visibility, Delete } from '@mui/icons-material'
import api from '../services/api'

const reportTypes = [
    { value: 'financial_health', label: 'Financial Health Report' },
    { value: 'risk_assessment', label: 'Risk Assessment Report' },
    { value: 'investor_ready', label: 'Investor Ready Report' },
    { value: 'tax_compliance', label: 'Tax Compliance Report' },
    { value: 'cash_flow_forecast', label: 'Cash Flow Forecast' },
]

export default function Reports() {
    const [loading, setLoading] = useState(true)
    const [reports, setReports] = useState<any[]>([])
    const [dialogOpen, setDialogOpen] = useState(false)
    const [generating, setGenerating] = useState(false)
    const [selectedType, setSelectedType] = useState('financial_health')

    useEffect(() => {
        loadReports()
    }, [])

    const loadReports = async () => {
        try {
            const response = await api.get('/api/reports')
            setReports(response.data.items || [])
        } catch {
            // Mock data
            setReports([
                { id: 1, title: 'Financial Health Report - Jan 2026', report_type: 'financial_health', generated_at: '2026-01-15', status: 'completed' },
                { id: 2, title: 'Risk Assessment Report', report_type: 'risk_assessment', generated_at: '2026-01-10', status: 'completed' },
                { id: 3, title: 'Investor Ready Report', report_type: 'investor_ready', generated_at: '2026-01-05', status: 'completed' },
            ])
        } finally {
            setLoading(false)
        }
    }

    const generateReport = async () => {
        setGenerating(true)
        try {
            await api.post('/api/reports/generate', { report_type: selectedType })
            setDialogOpen(false)
            loadReports()
        } catch (error) {
            console.error('Failed to generate report', error)
        } finally {
            setGenerating(false)
        }
    }

    const downloadReport = async (reportId: number, format: string) => {
        try {
            const response = await api.get(`/api/reports/${reportId}/export?format=${format}`, {
                responseType: 'blob'
            })
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.download = `report_${reportId}.${format}`
            link.click()
        } catch (error) {
            console.error('Download failed', error)
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
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" fontWeight={700}>
                    Reports
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => setDialogOpen(true)}
                >
                    Generate Report
                </Button>
            </Box>

            <Grid container spacing={3}>
                {reports.map((report) => (
                    <Grid item xs={12} md={6} lg={4} key={report.id}>
                        <Card className="card-hover">
                            <CardContent>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                    <Chip
                                        size="small"
                                        label={report.report_type.replace('_', ' ')}
                                        color="primary"
                                        variant="outlined"
                                    />
                                    <Chip
                                        size="small"
                                        label={report.status}
                                        color={report.status === 'completed' ? 'success' : 'warning'}
                                    />
                                </Box>
                                <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
                                    {report.title}
                                </Typography>
                                <Typography color="text.secondary" variant="body2" sx={{ mb: 2 }}>
                                    Generated: {new Date(report.generated_at).toLocaleDateString()}
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                    <Button
                                        size="small"
                                        startIcon={<Visibility />}
                                        variant="outlined"
                                    >
                                        View
                                    </Button>
                                    <Button
                                        size="small"
                                        startIcon={<Download />}
                                        variant="contained"
                                        onClick={() => downloadReport(report.id, 'pdf')}
                                    >
                                        PDF
                                    </Button>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            {/* Generate Report Dialog */}
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Generate New Report</DialogTitle>
                <DialogContent>
                    <FormControl fullWidth sx={{ mt: 2 }}>
                        <InputLabel>Report Type</InputLabel>
                        <Select
                            value={selectedType}
                            label="Report Type"
                            onChange={(e) => setSelectedType(e.target.value)}
                        >
                            {reportTypes.map((type) => (
                                <MenuItem key={type.value} value={type.value}>
                                    {type.label}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
                    <Button
                        variant="contained"
                        onClick={generateReport}
                        disabled={generating}
                    >
                        {generating ? <CircularProgress size={24} /> : 'Generate'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    )
}
