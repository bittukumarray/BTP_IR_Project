import React, { Component } from 'react';
import Paper from '@material-ui/core/Paper';
import InputBase from '@material-ui/core/InputBase';
import IconButton from '@material-ui/core/IconButton';
import SearchIcon from '@material-ui/icons/Search';
import Grid from '@material-ui/core/Grid';
import { withStyles } from "@material-ui/core/styles";
import axios from "axios";
import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
// import CardMedia from '@material-ui/core/CardMedia';
// import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';


const useStyles = theme => ({
    card: {
        alignItems: 'center',
        alignContent: 'center',
    },
    root: {
        padding: '2px 4px',
        display: 'flex',
        alignItems: 'center',
        alignContent: 'center',
        width: 400
    },
    input: {
        marginLeft: theme.spacing(1),
        flex: 1,
    },
    iconButton: {
        padding: 10,
    },
});

class SearchForm extends Component {

    state = { "query": "", "isSubmit": false };

    onChangeHandler = (e) => {
        this.setState({ "query": e.target.value })
        // console.log("in change ", e.target.value);
    }

    onFormSubmit = async (e) => {
        e.preventDefault();
        if (this.state.query.length > 0) {
            const header = {
                'Content-Type': 'application/json'
            }

            const body = {
                query: this.state.query
            }

            const result = await axios.post("http://localhost:8000/search/get-docs/", body, header);
            console.log(result.data);
            this.setState({ "result": result.data, isSubmit: true });

        }
        // console.log("form data is ", this.state.query);
    }

    render() {
        const { classes } = this.props;
        // console.log("usestyle is ", classes);

        return (
            <div>
                <form onSubmit={this.onFormSubmit}>
                    <Grid container
                        spacing={0}
                        direction="column"
                        alignItems="center"
                        justify="center"
                        style={this.state.isSubmit ? { minHeight: '20vh' } : { minHeight: '100vh' }}>
                        <Grid item xs={3}>
                            <Paper className={classes.root}>
                                <InputBase
                                    className={classes.input}
                                    placeholder="Enter query"
                                    fullWidth
                                    value={this.state.query}
                                    onChange={this.onChangeHandler}
                                />
                                <IconButton className={classes.iconButton} aria-label="search">
                                    <SearchIcon />
                                </IconButton>
                            </Paper>
                        </Grid>
                    </Grid>
                </form>
        {this.state.isSubmit ? <div><p>{this.state.result.length} results fetched</p>{this.state.result.map((element, index) =>
                    <Card className={classes.card} key={index} style={{"margin":"10px", "padding":'5px'}}>
                        <CardActionArea>
                            <CardContent>
                                <Typography gutterBottom variant="h5" component="h2">
                                <a href={element.url}>{element.title}</a>
                </Typography>
                                <Typography variant="body2" color="textSecondary" component="p">
                                    {element.question}
                </Typography>
                            </CardContent>
                        </CardActionArea>
                        <CardActions>
                            
                <a href={element.url}>{element.url}</a>
                        </CardActions>
                    </Card>
                )}</div> : null
                }
            </div>

        );
    }
}

export default withStyles(useStyles)(SearchForm)