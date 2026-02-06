import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import {
    Box,
    Card,
    CardContent,
    Typography,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Switch,
    FormControlLabel,
    Divider,
    Button,
    Alert,
} from '@mui/material'

export default function Settings() {
    const { t, i18n } = useTranslation()
    const [language, setLanguage] = useState(i18n.language)
    const [notifications, setNotifications] = useState(true)
    const [darkMode, setDarkMode] = useState(false)
    const [saved, setSaved] = useState(false)

    const handleLanguageChange = (lang: string) => {
        setLanguage(lang)
        i18n.changeLanguage(lang)
    }

    const handleSave = () => {
        // Save settings to backend
        setSaved(true)
        setTimeout(() => setSaved(false), 3000)
    }

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" fontWeight={700} sx={{ mb: 3 }}>
                {t('settings')}
            </Typography>

            {saved && (
                <Alert severity="success" sx={{ mb: 3 }}>
                    Settings saved successfully
                </Alert>
            )}

            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                        Language & Region
                    </Typography>
                    <FormControl fullWidth sx={{ mb: 2 }}>
                        <InputLabel>Language</InputLabel>
                        <Select
                            value={language}
                            label="Language"
                            onChange={(e) => handleLanguageChange(e.target.value)}
                        >
                            <MenuItem value="en">English</MenuItem>
                            <MenuItem value="hi">हिन्दी (Hindi)</MenuItem>
                        </Select>
                    </FormControl>
                </CardContent>
            </Card>

            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                        Notifications
                    </Typography>
                    <FormControlLabel
                        control={
                            <Switch
                                checked={notifications}
                                onChange={(e) => setNotifications(e.target.checked)}
                            />
                        }
                        label="Email notifications for reports"
                    />
                    <Divider sx={{ my: 2 }} />
                    <FormControlLabel
                        control={<Switch defaultChecked />}
                        label="Risk alerts"
                    />
                </CardContent>
            </Card>

            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                        Appearance
                    </Typography>
                    <FormControlLabel
                        control={
                            <Switch
                                checked={darkMode}
                                onChange={(e) => setDarkMode(e.target.checked)}
                            />
                        }
                        label="Dark mode"
                    />
                </CardContent>
            </Card>

            <Button variant="contained" size="large" onClick={handleSave}>
                {t('save')}
            </Button>
        </Box>
    )
}
