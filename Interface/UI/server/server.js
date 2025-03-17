import axios from 'axios';

const getData = async (data) => {
    const response = await axios.get('http://localhost:8002', {...data});
    console.log(response);
    return response;
}

export {
    getData
};