import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useTranslation } from 'react-i18next'
import {
    Box,
    Card,
    CardContent,
    Typography,
    Button,
    LinearProgress,
    Alert,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Chip,
} from '@mui/material'
import { CloudUpload, InsertDriveFile, CheckCircle, Error } from '@mui/icons-material'
import api from '../services/api'

interface UploadedFile {
    id?: number
    name: string
    status: 'pending' | 'uploading' | 'success' | 'error'
    progress: number
    error?: string
}

export default function Upload() {
    const { t } = useTranslation()
    const [files, setFiles] = useState<UploadedFile[]>([])
    const [error, setError] = useState('')

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        setError('')

        const newFiles: UploadedFile[] = acceptedFiles.map(f => ({
            name: f.name,
            status: 'pending',
            progress: 0,
        }))

        setFiles(prev => [...prev, ...newFiles])

        // Upload each file
        for (let i = 0; i < acceptedFiles.length; i++) {
            const file = acceptedFiles[i]
            const fileIndex = files.length + i

            try {
                setFiles(prev => prev.map((f, idx) =>
                    idx === fileIndex ? { ...f, status: 'uploading', progress: 30 } : f
                ))

                const formData = new FormData()
                formData.append('file', file)

                const response = await api.post('/api/upload', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' },
                    onUploadProgress: (progressEvent) => {
                        const progress = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1))
                        setFiles(prev => prev.map((f, idx) =>
                            idx === fileIndex ? { ...f, progress } : f
                        ))
                    }
                })

                setFiles(prev => prev.map((f, idx) =>
                    idx === fileIndex ? { ...f, status: 'success', progress: 100, id: response.data.id } : f
                ))
            } catch (err: any) {
                setFiles(prev => prev.map((f, idx) =>
                    idx === fileIndex ? {
                        ...f,
                        status: 'error',
                        error: err.response?.data?.detail || 'Upload failed'
                    } : f
                ))
            }
        }
    }, [files.length])

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'text/csv': ['.csv'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
            'application/pdf': ['.pdf'],
        },
        maxSize: 10 * 1024 * 1024, // 10MB
    })

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" fontWeight={700} sx={{ mb: 3 }}>
                {t('uploadTitle')}
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
                    {error}
                </Alert>
            )}

            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Box
                        {...getRootProps()}
                        sx={{
                            p: 6,
                            border: '2px dashed',
                            borderColor: isDragActive ? 'primary.main' : 'divider',
                            borderRadius: 3,
                            bgcolor: isDragActive ? 'action.hover' : 'background.default',
                            textAlign: 'center',
                            cursor: 'pointer',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                                borderColor: 'primary.main',
                                bgcolor: 'action.hover',
                            },
                        }}
                    >
                        <input {...getInputProps()} />
                        <CloudUpload sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                        <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
                            {t('dragDrop')}
                        </Typography>
                        <Typography color="text.secondary" sx={{ mb: 2 }}>
                            {t('supportedFormats')}
                        </Typography>
                        <Button variant="contained">
                            Select Files
                        </Button>
                    </Box>
                </CardContent>
            </Card>

            {files.length > 0 && (
                <Card>
                    <CardContent>
                        <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                            Uploaded Files
                        </Typography>
                        <List>
                            {files.map((file, index) => (
                                <ListItem key={index} divider>
                                    <ListItemIcon>
                                        {file.status === 'success' ? (
                                            <CheckCircle color="success" />
                                        ) : file.status === 'error' ? (
                                            <Error color="error" />
                                        ) : (
                                            <InsertDriveFile color="primary" />
                                        )}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={file.name}
                                        secondary={
                                            file.status === 'uploading' ? (
                                                <LinearProgress
                                                    variant="determinate"
                                                    value={file.progress}
                                                    sx={{ mt: 1 }}
                                                />
                                            ) : file.error ? (
                                                <Typography color="error" variant="caption">
                                                    {file.error}
                                                </Typography>
                                            ) : null
                                        }
                                    />
                                    <Chip
                                        size="small"
                                        label={file.status}
                                        color={
                                            file.status === 'success' ? 'success' :
                                                file.status === 'error' ? 'error' :
                                                    file.status === 'uploading' ? 'primary' : 'default'
                                        }
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </CardContent>
                </Card>
            )}
        </Box>
    )
}
