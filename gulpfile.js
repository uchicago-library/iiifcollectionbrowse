'use strict';

var gulp = require('gulp');
var sass = require('gulp-sass');
var browserSync = require('browser-sync').create();


gulp.task('sass', function(){
  return gulp.src('iiifcollectionbrowse/static/css/**/*.scss')
    .pipe(sass())
    .pipe(gulp.dest('iiifcollectionbrowse/static/css'))
});

gulp.task('watch', ['sass'], function(){
  gulp.watch('iiifcollectionbrowse/static/css/**/*.scss', ['sass']);
})

gulp.task("default", ["sass", "watch"], function() {
});
