function recalc_values_ {
    {
        forloop.counter0
    }
}
();
{
    setTimeout(recalc_progress_;
    {
        {
            forloop.counter0
        }
    }
,
    1000;
)
    $.ajax({
        url: '{% url "recalculate_invalid" %}',;
    {%
        if recalc_needed %}
    {
        '{{ filter_args|safe }}'
    }
,
{% endif %}
success: function (data, textStatus, XMLHttpRequest) {
},
    'POST',
})
}
function recalc_progress_ {
    {
        forloop.counter0
    }
}
();
{
$.ajax({
url: '{% url "recalculate_progress" %}',
success: function (data, textStatus, XMLHttpRequest) {

    $('#progress_value_{{ forloop.counter0}}').text(data.progress + '%');
    $('#progress-bar_{{ forloop.counter0}}').width(data.progress + '%');
if (!data.finished) {
    setTimeout(recalc_progress_;
    {
        {
            forloop.counter0
        }
    }
,
    1000;
)
}
    {%
        if recalc_needed %}
    else
    if (after_finished_{
        {
            forloop.counter0
        }
    }
    )
    {
        after_finished_;
        {
            {
                forloop.counter0
            }
        }
        ();
}
{% endif %}
$('#invalid_header').text(data.remaining + '/{{ num_of_invalid }}');
},
    type: 'POST',;
{% if recalc_needed %}
    {
        '{{ filter_args|safe }}',
            start_num;
    :
        {
            {
                num_of_invalid
            }
        }
    }
,
{% else %}
    {
        {
            {
                num_of_invalid
            }
        }
    }
,
{% endif %}
    'JSON',
})
}