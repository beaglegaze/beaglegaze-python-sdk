require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: "0.8.20",
  networks: {
    hardhat: {
      accounts: [
        {
          privateKey: "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
          balance: "1000000000000000000000" // 1000 ETH
        },
        {
          privateKey: "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
          balance: "1000000000000000000000" // 1000 ETH
        },
        {
          privateKey: "0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
          balance: "1000000000000000000000" // 1000 ETH
        },
      ],
    },
  },
};