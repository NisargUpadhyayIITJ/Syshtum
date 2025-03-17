import axios from 'axios';

const getData = async (data) => {
    const response = await axios.post('http://127.0.0.1:8002/pipeline', {...data});
    console.log(response);
    return response.data;
}

export {
    getData
};