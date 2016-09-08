from django_assets import Bundle, register

js = Bundle('jquery/dist/jquery.js',
            'bootstrap-sass/assets/javascripts/bootstrap.js',
            filters='uglifyjs',
            output='app.js')
register('script', js)

css = Bundle('style/id.scss',
             filters='scss',
             depends=['**/*.scss'],
             output='style.css')
register('style', css)
