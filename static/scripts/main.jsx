import React from 'react';
import ReactDOM from 'react-dom';
import {Grid, Row, Col} from 'react-bootstrap';
import {Form, FormGroup, FormControl, Button} from 'react-bootstrap';
import axios from 'axios';
// import fetch from 'node-fetch';
import $ from "jquery";

class ProfilesTable extends React.Component {
  
  constructor(props){
    super(props);
    this.state = {profiles: "2"};
  }

  componentDidMount() {
    $.ajax({
        type: 'GET',
        url: '/profilesclusters.json',
        dataType: 'json',
        async: false,
        success: function(res){
          this.setState({profiles: res});
        }.bind(this),
        error: function(xhr, status, err) {
          console.error(status, err.toString());
        }.bind(this)
      });
  }

  render(){
    const data = this.state.profiles;
    return (<h1>{data}</h1>);  
  }
}

class ScatterPlot extends React.Component {

  render() {
    return (<h1>123</h1>);
  }

}

class InputSearch extends React.Component {
  
  constructor(props) {
    super(props);
    this.state = {value : ''};
    this.handleChange = this.handleChange.bind(this);
    this.handleClick = this.handleClick.bind(this); 
  }

  handleChange(e) {
    this.setState({value: e.target.value});
  }

  handleClick() {
    this.props.updateData(this.state.value);
  }

  render(){
    return (
          <Form>
            <FormGroup>
                <FormControl id="formInputSearch" type="text" placeholder="Search..." onChange={this.handleChange} />
            </FormGroup>
            <Button type="submit" onClick={this.handleClick}>Search</Button>
          </Form>
    );
  }
}

class App extends React.Component {

  constructor(props) {
    super(props);
    this.state = {data: {}};
    this.sendQuery = this.sendQuery.bind(this);
  }
  
  sendQuery(query) {
    if (query.trim() !== '') {
      $.ajax({
        type: 'POST',
        url: '/query',
        dataType: 'json',
        data: query,
        async: false,
        success: function(res){
          this.setState({data: res});
        }.bind(this),
        error: function(xhr, status, err) {
          console.error(status, err.toString());
        }.bind(this)
      });
    }
  }

  render() {
    return(
      <Grid>
        <Row className="show-grid">
          <Col md={2}></Col>
          <Col md={8}><h1>Linkedin Profiles Grouping Tool<small> by Larry</small></h1></Col>
        </Row>
        <Row className="show-grid">
          <Col md={1}></Col>
          <Col md={8}><h3>Please input query/keywords</h3></Col>
        </Row>
        <Row className="show-grid">
          <Col md={2}></Col>
          <Col md={8}><InputSearch updateData={this.sendQuery}/></Col>
        </Row>
        <Row className="show-grid">
          <Col md={1}></Col>
          <Col md={8}><h3>Retrieved Profiles Table</h3></Col>
        </Row>

        <Row className="show-grid">
          <Col md={2}></Col>
          <Col md={8}><ProfilesTable /></Col>
        </Row>

        <Row className="show-grid">
          <Col md={1}></Col>
          <Col md={8}><h3></h3></Col>
        </Row>

        <Row className="show-grid">
          <Col md={2}></Col>
          <Col md={8}><ScatterPlot /></Col>
        </Row>
      </Grid>
    );
  }
}

ReactDOM.render(<App />, document.getElementById('root'));
