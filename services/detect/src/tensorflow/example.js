const fs = require('fs');
const tf = require('@tensorflow/tfjs-node');
const blazeface = require('@tensorflow-models/blazeface');


const run = async () => {
    const model = await blazeface.load();
    const data = fs.readFileSync(`${__dirname}/batman.jpg`);
    const tensor = tf.node.decodeImage(data, 3)
    const res = await model.estimateFaces(tensor)
    console.log('detection', JSON.stringify(res, null, 4))
}


run()
