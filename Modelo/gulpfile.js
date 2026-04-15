// Importa las funciones necesarias de Gulp para tareas de automatización
const { src, dest, watch, parallel } = require('gulp');
// Importa el compilador de Sass con soporte para la nueva API
const sass = require('gulp-sass')(require('sass'));
// Importa plumber para manejar errores sin detener el flujo de tareas
const plumber = require('gulp-plumber');
// Importa terser para minificar código JavaScript
const terser = require('gulp-terser');
// Importa sourcemaps para generar mapas de origen
const sourcemaps = require('gulp-sourcemaps');

// Función para compilar archivos SCSS a CSS
function css(done) {
    src('src/scss/**/*.scss')        // Selecciona todos los archivos .scss en src/scss/
        .pipe(sourcemaps.init())      // Inicializa mapas de origen
        .pipe(plumber())             // Previene que errores detengan la compilación
        .pipe(sass({ outputStyle: 'compressed' })) // Compila SCSS a CSS comprimido
        .pipe(sourcemaps.write('.')) // Escribe mapas de origen
        .pipe(dest('dist/css'));     // Guarda el CSS compilado en dist/css/
    done(); // Indica que la tarea ha terminado
}

// Función para minificar archivos JavaScript
function javascript(done) {
    src('src/js/**/*.js')           // Selecciona todos los archivos .js en src/js/
        .pipe(sourcemaps.init())     // Inicializa mapas de origen
        .pipe(plumber())            // Maneja errores sin detener el flujo
        .pipe(terser())             // Minifica el código JavaScript
        .pipe(sourcemaps.write('.')) // Escribe mapas de origen
        .pipe(dest('dist/js'));     // Guarda el JS minificado en dist/js/
    done(); // Indica que la tarea ha terminado
}

// Función para modo desarrollo con watchers
function dev(done) {
    watch('src/scss/**/*.scss', css); // Vigila cambios en SCSS y ejecuta css()
    watch('src/js/**/*.js', javascript); // Vigila cambios en JS y ejecuta javascript()
    done(); // Indica que la tarea ha terminado
}

// Exporta las funciones para usar desde línea de comandos
exports.css = css;              // Permite ejecutar 'gulp css'
exports.js = javascript;        // Permite ejecutar 'gulp js'
exports.dev = parallel(css, javascript, dev); // Ejecuta todas las tareas en paralelo
