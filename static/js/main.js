// Funciones JavaScript adicionales
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de Evaluación de Inglés cargado');
    
    // Auto-dismiss alerts
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Función para mostrar detalles de evaluación
function verDetalle(id) {
    // Implementar visualización de detalles
    console.log('Ver detalle de evaluación:', id);
}

// Función para validar respuesta
function validarRespuesta(textarea) {
    const valor = textarea.value.trim();
    const minLength = 20;
    
    if (valor.length < minLength) {
        textarea.classList.add('is-invalid');
        return false;
    } else {
        textarea.classList.remove('is-invalid');
        textarea.classList.add('is-valid');
        return true;
    }
}