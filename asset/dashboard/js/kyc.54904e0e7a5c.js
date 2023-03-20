$(document).on("submit", "#kycForm", function (e) {
    e.preventDefault()
   
    buttonObj = $(this).find("center button")
    origButtonText = buttonObj.html()
    buttonObj.html("submitting...")

    //send ajax
    form = $(this)
    data = new FormData(form[0])
    fileInputs = $("input[type=file]")
    if(fileInputs.length > 0){
        for(i = 0;i < fileInputs.length ;i++){
            element = $(fileInputs[i])
            data[element.attr("name")] = element.get(0).files[0]
        }
      
    }
   
   
    $.ajax({
        
        type: "POST",
        url: form.attr("action"),
        data: data,
        processData: false,
        contentType: false,
        timeout : 3000,
        success: function (response) {
            if(response.success){
               alert("Your kyc application was submitted successfuly, you would be informed on the progress of your application.")
                url = response.success_url
                window.location.href = url
            }

            if(response.error){
               //console.log(response.error_response)
                alert("correct the form errors.")
                buttonObj.html(origButtonText)
                handleFormError(form, response.error_response)
            }
          
        },
        error : function(){
       
            alert("Something went wrong, please  retry or contact support.")
            buttonObj.html(origButtonText)
        },
        statusCode: {
            400: function (response) {
                handleFormError(form, response.responseJSON)
            }
        }

    })
})