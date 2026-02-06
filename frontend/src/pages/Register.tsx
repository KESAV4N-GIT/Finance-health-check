import { useState } from 'react'
import { useNavigate, Link as RouterLink } from 'react-router-dom'
import {
    Box,
    Card,
    CardContent,
    TextField,
    Button,
    Typography,
    Link,
    Alert,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    CircularProgress,
} from '@mui/material'
import { TrendingUp } from '@mui/icons-material'
import api from '../services/api'

interface RegisterProps {
    onLogin: (token: string, refreshToken: string) => void
}

const industries = [
    { value: 'manufacturing', label: 'Manufacturing' },
    { value: 'retail', label: 'Retail' },
    { value: 'agriculture', label: 'Agriculture' },
    { value: 'services', label: 'Services' },
    { value: 'logistics', label: 'Logistics' },
    { value: 'ecommerce', label: 'E-commerce' },
]

export default function Register({ onLogin }: RegisterProps) {
    const navigate = useNavigate()
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        company_name: '',
        industry_type: 'services',
    })
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleChange = (field: string, value: string) => {
        setFormData({ ...formData, [field]: value })
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match')
            return
        }

        setLoading(true)

        try {
            await api.post('/auth/register', {
                email: formData.email,
                password: formData.password,
                company_name: formData.company_name,
                industry_type: formData.industry_type,
            })

            // Auto-login after registration
            const loginResponse = await api.post('/auth/login', {
                email: formData.email,
                password: formData.password,
            })
            onLogin(loginResponse.data.access_token, loginResponse.data.refresh_token)
            navigate('/')
        } catch (err: any) {
            console.error('Registration Error:', err);
            const errorMessage = err.response?.data?.detail || err.message || 'Registration failed. Please try again.';
            setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
        } finally {
            setLoading(false)
        }
    }

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'linear-gradient(135deg, #1e3a5f 0%, #2563eb 50%, #7c3aed 100%)',
                p: 2,
            }}
        >
            <Card sx={{ maxWidth: 480, width: '100%', p: 2 }}>
                <CardContent>
                    <Box sx={{ textAlign: 'center', mb: 4 }}>
                        <Box
                            sx={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                width: 60,
                                height: 60,
                                borderRadius: 2,
                                background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
                                mb: 2,
                            }}
                        >
                            <TrendingUp sx={{ color: 'white', fontSize: 32 }} />
                        </Box>
                        <Typography variant="h4" fontWeight={700}>
                            Create Account
                        </Typography>
                        <Typography color="text.secondary" sx={{ mt: 1 }}>
                            Start your financial health journey
                        </Typography>
                    </Box>

                    {error && (
                        <Alert severity="error" sx={{ mb: 3 }}>
                            {error}
                        </Alert>
                    )}

                    <form onSubmit={handleSubmit}>
                        <TextField
                            fullWidth
                            label="Company Name"
                            value={formData.company_name}
                            onChange={(e) => handleChange('company_name', e.target.value)}
                            required
                            sx={{ mb: 2 }}
                        />
                        <FormControl fullWidth sx={{ mb: 2 }}>
                            <InputLabel>Industry</InputLabel>
                            <Select
                                value={formData.industry_type}
                                label="Industry"
                                onChange={(e) => handleChange('industry_type', e.target.value)}
                            >
                                {industries.map((ind) => (
                                    <MenuItem key={ind.value} value={ind.value}>
                                        {ind.label}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                        <TextField
                            fullWidth
                            label="Email"
                            type="email"
                            value={formData.email}
                            onChange={(e) => handleChange('email', e.target.value)}
                            required
                            sx={{ mb: 2 }}
                        />
                        <TextField
                            fullWidth
                            label="Password"
                            type="password"
                            value={formData.password}
                            onChange={(e) => handleChange('password', e.target.value)}
                            required
                            sx={{ mb: 2 }}
                            helperText="Minimum 8 characters"
                        />
                        <TextField
                            fullWidth
                            label="Confirm Password"
                            type="password"
                            value={formData.confirmPassword}
                            onChange={(e) => handleChange('confirmPassword', e.target.value)}
                            required
                            sx={{ mb: 3 }}
                        />
                        <Button
                            type="submit"
                            variant="contained"
                            fullWidth
                            size="large"
                            disabled={loading}
                            sx={{ mb: 2, py: 1.5 }}
                        >
                            {loading ? <CircularProgress size={24} /> : 'Create Account'}
                        </Button>
                    </form>

                    <Typography textAlign="center" color="text.secondary">
                        Already have an account?{' '}
                        <Link component={RouterLink} to="/login">
                            Sign in
                        </Link>
                    </Typography>
                </CardContent>
            </Card>
        </Box>
    )
}
