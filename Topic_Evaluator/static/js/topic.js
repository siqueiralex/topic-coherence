
class FormHandler{

    constructor(){
        this.topic = null;
        this.wordlist = null;
        this.topic_changed();
        this.stemmed = false;
    }

    submit(){
        $('#result').html('')
        if($("#stemmed").is(":checked")){
            this.stemmed = true;
        }else{
            this.stemmed = false;
        }
        if(this.wordlist.length > 1){
            $('#spinner').addClass("lds-spinner");
            this.evaluate_topic( data => {
                $('#spinner').removeClass("lds-spinner")
                console.log( 'data:',data);
                let str = "";
                for(var index in data) {
                    str = str + index + ":  " + data[index] + "<br>";
                }
                
                $('#result').html(str)
            });    
        }
    }

    topic_changed(){
        this.topic = $('#topic').val();
        this.wordlist = this.topic.split(" ");

        if(this.wordlist.length > 1){
            $("#btnSubmit").attr("disabled", false);
        }else{
            $("#btnSubmit").attr("disabled", true);   
        }
    }

    evaluate_topic(callback){

        $.ajax({
            type: 'POST',
            url: "/api/topic/",
            data: {
                 topic: this.topic,
                 stemmed: this.stemmed
            },
            success: function(data) {
               callback(data);
            }
        });
    }
}