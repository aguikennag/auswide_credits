
function handleFormError(form_object,error_response){
    //apply error
    for(const [field,error] of Object.entries(error_response)){
       $(".field-error[input-name=" + field + "]").html(error)
    
    }
    dangerText = "please correct the form errors"
    
    //check for general errors
    if (error_response.non_field_errors){
        errorText = error_response.non_field_errors
        alert(errorText)
    }
  
}