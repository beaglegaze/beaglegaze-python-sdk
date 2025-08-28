// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UsageContract {
    mapping(address => bool) private developers;
    address[] private developerList;
    mapping(address => bool) private clients;
    mapping(address => uint256) public clientFunding;
    mapping(address => uint256) private developerBalances;

    // Voting system for developer registration
    mapping(address => bool) private pendingRegistrations;
    mapping(address => mapping(address => bool)) private votes;
    mapping(address => mapping(address => bool)) private hasVoted;
    mapping(address => uint256) private voteCount;

    event DeveloperRegistered(address indexed developer);
    event ClientRegistered(address indexed client);
    event Funded(address indexed client, uint256 amount);
    event Consumed(address indexed client, uint256 amount);

    constructor() {
        developers[msg.sender] = true;
        developerList.push(msg.sender);
        emit DeveloperRegistered(msg.sender);
    }

    function requestDeveloperRegistration() external {
        require(!developers[msg.sender], "Already registered as developer");
        require(!pendingRegistrations[msg.sender], "Registration already pending");

        pendingRegistrations[msg.sender] = true;
        // Do not add to developerList or emit event yet - wait for voting
    }

    function hasPendingRegistrationRequest(address developer) external view returns (bool) {
        return pendingRegistrations[developer];
    }

    function voteForDeveloper(address developer, bool approve) external {
        require(developers[msg.sender], "Only developers can vote");
        require(pendingRegistrations[developer], "No pending registration for this developer");
        require(!hasVoted[developer][msg.sender], "Already voted for this developer");

        votes[developer][msg.sender] = approve;
        hasVoted[developer][msg.sender] = true;
        voteCount[developer]++;

        // Check if all developers have voted
        if (voteCount[developer] == developerList.length) {
            _finalizeVoting(developer);
        }
    }

    function _finalizeVoting(address developer) private {
        uint256 approvalCount = 0;

        // Count approval votes
        for (uint256 i = 0; i < developerList.length; i++) {
            if (votes[developer][developerList[i]]) {
                approvalCount++;
            }
        }

        // Require majority (>50%) approval
        bool approved = approvalCount * 2 > developerList.length;

        if (approved) {
            developers[developer] = true;
            developerList.push(developer);
            emit DeveloperRegistered(developer);
        }

        // Clean up voting data
        pendingRegistrations[developer] = false;
        voteCount[developer] = 0;
        for (uint256 i = 0; i < developerList.length; i++) {
            delete votes[developer][developerList[i]];
            delete hasVoted[developer][developerList[i]];
        }
    }

    function registerClient() external {
        clients[msg.sender] = true;
        emit ClientRegistered(msg.sender);
    }

    function isDeveloper() external view returns (bool) {
        return developers[msg.sender];
    }

    function isClient(address user) external view returns (bool) {
        return clients[user];
    }

    function fund() external payable {
        require(msg.value > 0, "No funds sent");
        clients[msg.sender] = true;
        clientFunding[msg.sender] += msg.value;
        emit Funded(msg.sender, msg.value);
    }

    function getClientFunding() external view returns (uint256) {
        return clientFunding[msg.sender];
    }

    function requestPayout() external {
        require(clients[msg.sender], "Only clients can request payout");
        require(clientFunding[msg.sender] > 0, "No funds available for payout");

        uint256 amount = clientFunding[msg.sender];

        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent, "Failed to send payout");

        clientFunding[msg.sender] = 0;
    }

    function consume(uint256 amount) external returns (uint256) {
        emit Consumed(msg.sender, clientFunding[msg.sender]);
        require(
            clientFunding[msg.sender] >= amount,
            "Insufficient client funding"
        );
        require(developerList.length > 0, "No developers registered");
        clientFunding[msg.sender] -= amount;
        uint256 share = amount / developerList.length;
        uint256 remainder = amount % developerList.length;
        for (uint256 i = 0; i < developerList.length; i++) {
            developerBalances[developerList[i]] += share;
        }
        if (remainder > 0) {
            developerBalances[developerList[0]] += remainder;
        }
        return clientFunding[msg.sender];
    }

    function getDeveloperBalance() external view returns (uint256) {
        require(developers[msg.sender], "Only developers can check their balance");
        return developerBalances[msg.sender];
    }

    function withdrawBalance() external {
        require(developers[msg.sender], "Only developers can withdraw");
        uint256 balance = developerBalances[msg.sender];
        require(balance > 0, "No balance to withdraw");

        developerBalances[msg.sender] = 0;
        (bool sent, ) = msg.sender.call{value: balance}("");
        require(sent, "Failed to withdraw balance");
    }
}
