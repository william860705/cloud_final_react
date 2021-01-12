
const React = require("react");
const { withRouter } = require("react-router-dom");
// import { JsonToTable } from "react-json-to-table";
const JsonTable = require('ts-react-json-table');
class History extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            data: [
                
            ]
        };

    }
    componentDidMount() {
        fetch(`http://localhost:5000/debug`)
      .then(res => res.json())
      .then((result) => {
        console.log(result);
        this.setState({
            data: result.users
        })
      },
      (error) => {
        console.log(error);
      });

     }
  


    render() {
        const divStyle = {
            
        };
        return (
        <div className="App" style={divStyle}>
            <p></p>
            <JsonTable rows = {this.state.data} />

            </div>
                );
    }
}

module.exports = History;