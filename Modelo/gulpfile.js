const { src, dest, watch, parallel } = require('gulp');
const sass = require('gulp-sass')(require('sass'));
const plumber = require('gulp-plumber');
const terser = require('gulp-terser');
const sourcemaps = require('gulp-sourcemaps');

function css(done) {
    src('src/scss/**/*.scss')        // Identificar el archivo .SCSS a compilar
        .pipe(sourcemaps.init())
        .pipe(plumber())             // Evitar que el flujo de compilación se detenga por errores
        .pipe(sass({ outputStyle: 'compressed' })) // Compilarlo
        .pipe(sourcemaps.write('.'))
        .pipe(dest('dist/css'));     // Almacenarla en el disco duro
    done();
}

function javascript(done) {
    src('src/js/**/*.js')
        .pipe(sourcemaps.init())
        .pipe(plumber())
        .pipe(terser())              // Comprimir el código JS
        .pipe(sourcemaps.write('.'))
        .pipe(dest('dist/js'));      // Guardar el código JS en el disco duro
    done();
}

function dev(done) {
    watch('src/scss/**/*.scss', css);
    watch('src/js/**/*.js', javascript);
    done();
}

exports.css = css;
exports.js = javascript;
exports.dev = parallel(css, javascript, dev);
