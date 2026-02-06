import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

const resources = {
    en: {
        translation: {
            // Navigation
            dashboard: 'Dashboard',
            upload: 'Upload',
            riskAssessment: 'Risk Assessment',
            reports: 'Reports',
            settings: 'Settings',
            logout: 'Logout',

            // Dashboard
            financialHealth: 'Financial Health',
            healthScore: 'Health Score',
            revenue: 'Revenue',
            expenses: 'Expenses',
            netProfit: 'Net Profit',
            cashFlow: 'Cash Flow',

            // Risk
            overallRisk: 'Overall Risk',
            liquidityRisk: 'Liquidity Risk',
            solvencyRisk: 'Solvency Risk',
            operationalRisk: 'Operational Risk',
            low: 'Low',
            medium: 'Medium',
            high: 'High',

            // Upload
            uploadTitle: 'Upload Financial Statements',
            dragDrop: 'Drag and drop files here, or click to select',
            supportedFormats: 'Supported formats: CSV, XLSX, PDF',
            processing: 'Processing...',
            uploadSuccess: 'File uploaded successfully',

            // Actions
            viewDetails: 'View Details',
            download: 'Download',
            generateReport: 'Generate Report',
            refresh: 'Refresh',

            // Status
            healthy: 'Healthy',
            caution: 'Caution',
            critical: 'Critical',

            // Tooltips
            currentRatioTooltip: 'Current Ratio measures short-term liquidity (Current Assets / Current Liabilities)',
            debtToEquityTooltip: 'Debt to Equity shows leverage level (Total Debt / Total Equity)',

            // Common
            loading: 'Loading...',
            error: 'An error occurred',
            retry: 'Retry',
            save: 'Save',
            cancel: 'Cancel',
        }
    },
    hi: {
        translation: {
            // Navigation
            dashboard: 'डैशबोर्ड',
            upload: 'अपलोड',
            riskAssessment: 'जोखिम मूल्यांकन',
            reports: 'रिपोर्ट',
            settings: 'सेटिंग्स',
            logout: 'लॉग आउट',

            // Dashboard
            financialHealth: 'वित्तीय स्वास्थ्य',
            healthScore: 'स्वास्थ्य स्कोर',
            revenue: 'राजस्व',
            expenses: 'खर्च',
            netProfit: 'शुद्ध लाभ',
            cashFlow: 'नकदी प्रवाह',

            // Risk
            overallRisk: 'समग्र जोखिम',
            liquidityRisk: 'तरलता जोखिम',
            solvencyRisk: 'शोधनक्षमता जोखिम',
            operationalRisk: 'परिचालन जोखिम',
            low: 'कम',
            medium: 'मध्यम',
            high: 'उच्च',

            // Upload
            uploadTitle: 'वित्तीय विवरण अपलोड करें',
            dragDrop: 'फ़ाइलें यहाँ खींचें और छोड़ें, या चुनने के लिए क्लिक करें',
            supportedFormats: 'समर्थित प्रारूप: CSV, XLSX, PDF',
            processing: 'प्रसंस्करण...',
            uploadSuccess: 'फ़ाइल सफलतापूर्वक अपलोड हुई',

            // Status
            healthy: 'स्वस्थ',
            caution: 'सावधानी',
            critical: 'गंभीर',

            // Common
            loading: 'लोड हो रहा है...',
            error: 'एक त्रुटि हुई',
            retry: 'पुनः प्रयास करें',
            save: 'सहेजें',
            cancel: 'रद्द करें',
        }
    }
}

i18n
    .use(initReactI18next)
    .init({
        resources,
        lng: 'en',
        fallbackLng: 'en',
        interpolation: {
            escapeValue: false
        }
    })

export default i18n
