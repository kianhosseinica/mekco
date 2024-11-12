// static/admin/js/pricing_rule.js

(function($) {
    $(document).ready(function() {
        $('#id_category').change(function() {
            var categoryId = $(this).val();
            if (categoryId) {
                $.ajax({
                    url: '/ecommerce/admin/load-parent-category/',
                    data: {
                        'category_id': categoryId
                    },
                    success: function(data) {
                        $('#id_parent_category').empty();
                        if (data.parent_category) {
                            $('#id_parent_category').append('<option value="' + data.parent_category.id + '">' + data.parent_category.name + '</option>');
                        } else {
                            $('#id_parent_category').append('<option value="">No parent category</option>');
                        }
                    }
                });

                $.ajax({
                    url: '/ecommerce/admin/load-subcategories/',
                    data: {
                        'category_id': categoryId
                    },
                    success: function(data) {
                        $('#id_subcategory').empty();
                        $('#id_subcategory').append('<option value="">Select subcategory</option>');
                        $.each(data.subcategories, function(key, value) {
                            $('#id_subcategory').append('<option value="' + value.id + '">' + value.name + '</option>');
                        });
                    }
                });
            } else {
                $('#id_parent_category').empty();
                $('#id_parent_category').append('<option value="">Select parent category</option>');

                $('#id_subcategory').empty();
                $('#id_subcategory').append('<option value="">Select subcategory</option>');
            }
        });
    });
})(django.jQuery);
