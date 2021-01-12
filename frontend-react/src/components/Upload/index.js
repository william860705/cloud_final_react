
const React = require("react");

class Upload extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            fig1: null,
            fig2: null,
            acc: null,
            loss: null,
            uploading: false
        };
        // this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    componentDidMount() {
        fetch(`http://localhost:5000/debug`)
      .then(res => res.json())
      .then((result) => {
        console.log(result);
      },
      (error) => {
        console.log(error);
      });

     }
    handleSubmit = async function(event){
        if (this.state.file !== null) {
            URL.revokeObjectURL(this.state.file);
        }
        
        // console.log(event);
        event.preventDefault();
        
        // Uncomment this if you wish to preview the image right after selection
        // this.setState({
        //     file: URL.createObjectURL(event.target.files[0]),
        //     uploading: true
        // });

        // Create a FormData to POST to backend
        const files = Array.from(event.target[0].files);
        const epoch = event.target[1].value;
        const lr = event.target[2].value;
        const elasticNetParam = event.target[3].value;
        const formData = new FormData();
        formData.append("file", files[0]); // key - value
        formData.append("epoch", epoch);
        formData.append("lr", lr);
        formData.append("elasticNetParam", elasticNetParam);
        // console.log(formData)


        // Send to Flask
        const response = await fetch(`http://localhost:5000/`, {
            method: 'POST',
            body: formData,
            contentType: false,
            processData: false
        });
        const data = await response.json();
        // console.log(data);

        // const fig2= await fetch(`http://localhost:5000/get-image/figure_2`, {
        //     method: 'GET',
        //     contentType: false,
        //     processData: false
        // });
        // const data = await fig2.json();
        // console.log(data)
        this.setState({
            fig1: `data:image/jpeg;base64, ${data['fig1']}`,
            fig2: `data:image/jpeg;base64, ${data['fig2']}`,
            acc: data['acc'],
            loss: data['loss'],
            uploading: true
        }
        );
        
        // return false;
    }


    render() {
        // const mystyle = {
        //     color: "white",
        //     backgroundColor: "DodgerBlue",
        //     padding: "10px",
        //     fontFamily: "Arial"
        //   };
        const divStyle = {
            display: "flex",
            alignItems: "center"
        };
        const imgStyle = {
            marginLeft: "auto",
            marginRight: "auto"
        };        
        return (
            <div>
                <form onSubmit={this.handleSubmit}>
                    <input type="file" name="file" />
                    <br />
                    <label>Epoch:  </label>
                    <input type="text" name="epoch" required/>
                    <br />
                    <label>lr:  </label>
                    <input type="text" name="lr" required/>
                    <br />
                    <label>elasticNetParam:  </label>
                    <input type="text"  name="elasticNetParam" required/>
                    <br />
                    <input type="submit" />
                    <br />
                </form>
                <div id="display-result">
                    { this.state.loss &&<p>Loss: {this.state.loss}</p>}
                    { this.state.acc &&<p>Acc: {this.state.acc}</p>}
                    <div id="two-figs" style={divStyle}>
                        { this.state.fig1 && <img src={this.state.fig1} style={imgStyle} alt="jeye" height="auto" width="35%"/> }
                        { this.state.fig2 && <img src={this.state.fig2} style={imgStyle} alt="jeye" height="auto" width="45%"/> }
                    </div>
                </div>
            </div>
        );
    }
}

module.exports = Upload;